from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Vehicle

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