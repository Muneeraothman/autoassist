from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Vehicle, ScheduleItem, ServiceRecord

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "AutoAssist API is running"}


@app.get("/api/vehicle")
def get_vehicle(db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).first()
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
    return [
        {
            "id": item.id,
            "service_name": item.service_name,
            "interval_miles": item.interval_miles,
            "interval_months": item.interval_months,
            "severe_interval_miles": item.severe_interval_miles,
            "notes": item.notes,
        }
        for item in items
    ]


@app.get("/api/services")
def get_services(db: Session = Depends(get_db)):
    records = db.query(ServiceRecord).order_by(ServiceRecord.service_date).all()
    return [
        {
            "id": record.id,
            "schedule_item_id": record.schedule_item_id,
            "service_date": str(record.service_date),
            "mileage_at_service": record.mileage_at_service,
            "cost": float(record.cost) if record.cost is not None else None,
            "performed_by": record.performed_by,
            "notes": record.notes,
            "receipt_key": record.receipt_key,
        }
        for record in records
    ]