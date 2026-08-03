import logging
import os
import secrets
from datetime import date, datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

import email_utils
import s3_utils
from database import get_db
from engine import get_upcoming_maintenance
from models import EmailToken, User, Vehicle, ScheduleItem, ServiceRecord
from stats import compute_stats

app = FastAPI()
logger = logging.getLogger("autoassist")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


class MileageUpdate(BaseModel):
    mileage: int = Field(gt=0)


class ServiceCreate(BaseModel):
    schedule_item_id: int | None = None
    service_date: date
    mileage_at_service: int = Field(gt=0)
    cost: float | None = Field(default=None, ge=0)
    performed_by: str | None = None
    notes: str | None = None

    @field_validator("service_date")
    @classmethod
    def reject_future_date(cls, value):
        if value > date.today():
            raise ValueError("Service date cannot be in the future")
        return value


class UserRegister(BaseModel):
    email: str
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value):
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format")
        return value.lower()


class UserLogin(BaseModel):
    email: str
    password: str


class VehicleCreate(BaseModel):
    make: str
    model: str
    year: int
    vin: str | None = None
    current_mileage: int = Field(gt=0)


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ReceiptUploadRequest(BaseModel):
    content_type: str

    @field_validator("content_type")
    @classmethod
    def validate_image_content_type(cls, value):
        if value not in s3_utils.CONTENT_TYPE_EXTENSIONS:
            allowed = ", ".join(s3_utils.CONTENT_TYPE_EXTENSIONS)
            raise ValueError(f"Unsupported content type. Allowed: {allowed}")
        return value


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user


def get_owned_vehicle_or_404(db: Session, vehicle_id: int, current_user: User) -> Vehicle:
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle is None or vehicle.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


def create_email_token(db: Session, user_id: int, token_type: str, expire_hours: float) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expire_hours)
    db.add(EmailToken(user_id=user_id, token=token, token_type=token_type, expires_at=expires_at))
    db.commit()
    return token


def consume_email_token(db: Session, token: str, token_type: str) -> EmailToken:
    record = (
        db.query(EmailToken)
        .filter(EmailToken.token == token, EmailToken.token_type == token_type)
        .first()
    )
    now = datetime.now(timezone.utc)
    if record is None or record.used_at is not None or record.expires_at < now:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    record.used_at = now
    db.commit()
    return record


def get_service_or_404(db: Session, vehicle_id: int, service_id: int) -> ServiceRecord:
    record = (
        db.query(ServiceRecord)
        .filter(ServiceRecord.id == service_id, ServiceRecord.vehicle_id == vehicle_id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Service record not found")
    return record


def serialize_schedule_item(item: ScheduleItem) -> dict:
    return {
        "id": item.id,
        "service_name": item.service_name,
        "interval_miles": item.interval_miles,
        "interval_months": item.interval_months,
        "severe_interval_miles": item.severe_interval_miles,
        "notes": item.notes,
    }


def serialize_service(record: ServiceRecord) -> dict:
    return {
        "id": record.id,
        "schedule_item_id": record.schedule_item_id,
        "service_date": str(record.service_date),
        "mileage_at_service": record.mileage_at_service,
        "cost": float(record.cost) if record.cost is not None else None,
        "performed_by": record.performed_by,
        "notes": record.notes,
        "receipt_key": record.receipt_key,
    }


def check_mileage_sane(mileage_at_service: int, vehicle: Vehicle) -> None:
    if mileage_at_service > vehicle.current_mileage + 500:
        raise HTTPException(
            status_code=422,
            detail="Mileage at service is more than 500 miles ahead of current mileage",
        )


def serialize_vehicle(vehicle: Vehicle) -> dict:
    return {
        "id": vehicle.id,
        "make": vehicle.make,
        "model": vehicle.model,
        "year": vehicle.year,
        "vin": vehicle.vin,
        "current_mileage": vehicle.current_mileage,
        "mileage_updated_at": vehicle.mileage_updated_at,
        "avg_miles_per_day": float(vehicle.avg_miles_per_day),
    }


@app.get("/")
def read_root():
    return {"message": "AutoAssist API is running"}


@app.post("/api/auth/register", status_code=201)
def register(payload: UserRegister, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(
            status_code=409, detail="An account with this email already exists"
        )

    hashed_password = pwd_context.hash(payload.password)
    user = User(email=payload.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    verify_token = create_email_token(db, user.id, "verify_email", expire_hours=24)
    try:
        email_utils.send_verification_email(user.email, verify_token)
    except Exception:
        # Best-effort: SES sandbox mode rejects sends to unverified recipients,
        # which would otherwise turn every non-verified signup into a failed registration.
        logger.warning("Failed to send verification email to %s", user.email, exc_info=True)

    token = create_access_token(user.id)
    set_auth_cookie(response, token)

    return {"id": user.id, "email": user.email}


@app.get("/api/auth/verify-email", response_class=HTMLResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        record = consume_email_token(db, token, "verify_email")
    except HTTPException:
        return HTMLResponse("<h2>Invalid or expired verification link.</h2>", status_code=400)

    user = db.query(User).filter(User.id == record.user_id).first()
    user.email_verified = True
    db.commit()

    return HTMLResponse(
        "<h2>Email verified</h2>"
        f"<p>You can close this tab and return to "
        f"<a href='{email_utils.FRONTEND_BASE_URL}'>AutoAssist</a>.</p>"
    )


@app.post("/api/auth/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is not None:
        reset_token = create_email_token(db, user.id, "reset_password", expire_hours=1)
        try:
            email_utils.send_password_reset_email(user.email, reset_token)
        except Exception:
            logger.warning("Failed to send password reset email to %s", user.email, exc_info=True)

    return {"detail": "If that email is registered, a reset link has been sent."}


@app.post("/api/auth/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    record = consume_email_token(db, payload.token, "reset_password")

    user = db.query(User).filter(User.id == record.user_id).first()
    user.hashed_password = pwd_context.hash(payload.new_password)

    db.query(EmailToken).filter(
        EmailToken.user_id == user.id,
        EmailToken.token_type == "reset_password",
        EmailToken.used_at.is_(None),
    ).update({"used_at": datetime.now(timezone.utc)})

    db.commit()
    return {"detail": "Password has been reset. You can now log in."}


@app.post("/api/auth/login")
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(user.id)
    set_auth_cookie(response, token)

    return {"id": user.id, "email": user.email}


@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "email_verified": current_user.email_verified,
    }


@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"detail": "Logged out"}


@app.get("/api/vehicles")
def list_vehicles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == current_user.id).order_by(Vehicle.id).all()
    return [serialize_vehicle(v) for v in vehicles]


@app.post("/api/vehicles", status_code=201)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = Vehicle(
        user_id=current_user.id,
        make=payload.make,
        model=payload.model,
        year=payload.year,
        vin=payload.vin,
        current_mileage=payload.current_mileage,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return serialize_vehicle(vehicle)


@app.delete("/api/vehicles/{vehicle_id}", status_code=204)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = get_owned_vehicle_or_404(db, vehicle_id, current_user)
    db.delete(vehicle)
    db.commit()


@app.get("/api/vehicles/{vehicle_id}")
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = get_owned_vehicle_or_404(db, vehicle_id, current_user)
    return serialize_vehicle(vehicle)


@app.patch("/api/vehicles/{vehicle_id}/mileage")
def update_mileage(
    vehicle_id: int,
    update: MileageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = get_owned_vehicle_or_404(db, vehicle_id, current_user)
    now = datetime.now(timezone.utc)
    time_since_update = now - vehicle.mileage_updated_at
    miles_driven = update.mileage - vehicle.current_mileage

    if update.mileage < vehicle.current_mileage:
        raise HTTPException(status_code=422, detail="Mileage cannot decrease")

    if time_since_update.days >= 1:
        vehicle.avg_miles_per_day = miles_driven / time_since_update.days

    vehicle.current_mileage = update.mileage
    vehicle.mileage_updated_at = now

    db.commit()
    db.refresh(vehicle)

    return serialize_vehicle(vehicle)


@app.get("/api/vehicles/{vehicle_id}/schedule")
def get_schedule(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_vehicle_or_404(db, vehicle_id, current_user)
    items = (
        db.query(ScheduleItem)
        .filter(ScheduleItem.vehicle_id == vehicle_id)
        .order_by(ScheduleItem.id)
        .all()
    )
    return [serialize_schedule_item(item) for item in items]


@app.get("/api/vehicles/{vehicle_id}/stats")
def get_stats(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = get_owned_vehicle_or_404(db, vehicle_id, current_user)
    schedule_items = (
        db.query(ScheduleItem).filter(ScheduleItem.vehicle_id == vehicle_id).order_by(ScheduleItem.id).all()
    )
    service_records = db.query(ServiceRecord).filter(ServiceRecord.vehicle_id == vehicle_id).all()

    return compute_stats(vehicle, schedule_items, service_records)


@app.get("/api/vehicles/{vehicle_id}/upcoming")
def get_upcoming(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = get_owned_vehicle_or_404(db, vehicle_id, current_user)
    schedule_items = (
        db.query(ScheduleItem).filter(ScheduleItem.vehicle_id == vehicle_id).order_by(ScheduleItem.id).all()
    )
    service_records = db.query(ServiceRecord).filter(ServiceRecord.vehicle_id == vehicle_id).all()

    results = get_upcoming_maintenance(vehicle, schedule_items, service_records, date.today())

    status_rank = {"OVERDUE": 0, "DUE_SOON": 1, "OK": 2}
    results.sort(key=lambda r: (status_rank[r["status"]], r["due_date"] or date.min))

    return [
        {
            "schedule_item": serialize_schedule_item(entry["schedule_item"]),
            "due_date": str(entry["due_date"]) if entry["due_date"] else None,
            "due_miles": entry["due_miles"],
            "status": entry["status"],
            "days_remaining": entry["days_remaining"],
            "miles_remaining": entry["miles_remaining"],
        }
        for entry in results
    ]


@app.get("/api/vehicles/{vehicle_id}/services")
def get_services(
    vehicle_id: int,
    schedule_item_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_vehicle_or_404(db, vehicle_id, current_user)
    query = db.query(ServiceRecord).filter(ServiceRecord.vehicle_id == vehicle_id)
    if schedule_item_id is not None:
        query = query.filter(ServiceRecord.schedule_item_id == schedule_item_id)
    records = query.order_by(ServiceRecord.service_date.desc()).all()
    return [serialize_service(record) for record in records]


@app.post("/api/vehicles/{vehicle_id}/services", status_code=201)
def create_service(
    vehicle_id: int,
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = get_owned_vehicle_or_404(db, vehicle_id, current_user)
    check_mileage_sane(service.mileage_at_service, vehicle)

    new_record = ServiceRecord(
        vehicle_id=vehicle.id,
        schedule_item_id=service.schedule_item_id,
        service_date=service.service_date,
        mileage_at_service=service.mileage_at_service,
        cost=service.cost,
        performed_by=service.performed_by,
        notes=service.notes,
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return serialize_service(new_record)


@app.put("/api/vehicles/{vehicle_id}/services/{service_id}")
def update_service(
    vehicle_id: int,
    service_id: int,
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = get_owned_vehicle_or_404(db, vehicle_id, current_user)
    record = get_service_or_404(db, vehicle_id, service_id)
    check_mileage_sane(service.mileage_at_service, vehicle)

    record.schedule_item_id = service.schedule_item_id
    record.service_date = service.service_date
    record.mileage_at_service = service.mileage_at_service
    record.cost = service.cost
    record.performed_by = service.performed_by
    record.notes = service.notes

    db.commit()
    db.refresh(record)

    return serialize_service(record)


@app.delete("/api/vehicles/{vehicle_id}/services/{service_id}", status_code=204)
def delete_service(
    vehicle_id: int,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = get_service_or_404(db, vehicle_id, service_id)
    db.delete(record)
    db.commit()


@app.post("/api/vehicles/{vehicle_id}/services/{service_id}/receipt-upload-url")
def get_receipt_upload_url(
    vehicle_id: int,
    service_id: int,
    payload: ReceiptUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_vehicle_or_404(db, vehicle_id, current_user)
    record = get_service_or_404(db, vehicle_id, service_id)

    extension = s3_utils.CONTENT_TYPE_EXTENSIONS[payload.content_type]
    key = s3_utils.build_receipt_key(current_user.id, vehicle_id, service_id, extension)
    upload_url = s3_utils.generate_upload_url(key, payload.content_type)

    record.receipt_key = key
    db.commit()

    return {"upload_url": upload_url, "key": key}


@app.get("/api/vehicles/{vehicle_id}/services/{service_id}/receipt-url")
def get_receipt_view_url(
    vehicle_id: int,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_vehicle_or_404(db, vehicle_id, current_user)
    record = get_service_or_404(db, vehicle_id, service_id)

    if record.receipt_key is None:
        raise HTTPException(status_code=404, detail="No receipt uploaded for this service")

    return {"url": s3_utils.generate_view_url(record.receipt_key)}
