from datetime import date, datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from database import get_db
from engine import get_upcoming_maintenance
from models import Vehicle, ScheduleItem, ServiceRecord
from stats import compute_stats

app = FastAPI()


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


def get_vehicle_or_404(db: Session) -> Vehicle:
    vehicle = db.query(Vehicle).first()
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


def get_service_or_404(db: Session, service_id: int) -> ServiceRecord:
    record = db.query(ServiceRecord).filter(ServiceRecord.id == service_id).first()
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


@app.get("/")
def read_root():
    return {"message": "AutoAssist API is running"}


@app.get("/api/vehicle")
def get_vehicle(db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(db)
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


@app.patch("/api/vehicle/mileage")
def update_mileage(update: MileageUpdate, db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(db)
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


@app.get("/api/schedule")
def get_schedule(db: Session = Depends(get_db)):
    items = db.query(ScheduleItem).order_by(ScheduleItem.id).all()
    return [serialize_schedule_item(item) for item in items]


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(db)
    schedule_items = db.query(ScheduleItem).order_by(ScheduleItem.id).all()
    service_records = db.query(ServiceRecord).all()

    return compute_stats(vehicle, schedule_items, service_records)


@app.get("/api/upcoming")
def get_upcoming(db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(db)
    schedule_items = db.query(ScheduleItem).order_by(ScheduleItem.id).all()
    service_records = db.query(ServiceRecord).all()

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


@app.get("/api/services")
def get_services(schedule_item_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(ServiceRecord)
    if schedule_item_id is not None:
        query = query.filter(ServiceRecord.schedule_item_id == schedule_item_id)
    records = query.order_by(ServiceRecord.service_date.desc()).all()
    return [serialize_service(record) for record in records]


@app.post("/api/services", status_code=201)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(db)
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


@app.put("/api/services/{service_id}")
def update_service(service_id: int, service: ServiceCreate, db: Session = Depends(get_db)):
    record = get_service_or_404(db, service_id)
    vehicle = get_vehicle_or_404(db)
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


@app.delete("/api/services/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    record = get_service_or_404(db, service_id)
    db.delete(record)
    db.commit()
