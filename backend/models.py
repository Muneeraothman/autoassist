from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)
    vin = Column(Text)
    current_mileage = Column(Integer, nullable=False)
    mileage_updated_at = Column(DateTime(timezone=True), server_default=func.now())
    avg_miles_per_day = Column(Numeric(6, 2), default=30.0)


class ScheduleItem(Base):
    __tablename__ = "schedule_items"

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    service_name = Column(Text, nullable=False)
    interval_miles = Column(Integer)
    interval_months = Column(Integer)
    severe_interval_miles = Column(Integer)
    notes = Column(Text)


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    schedule_item_id = Column(Integer, ForeignKey("schedule_items.id"))
    service_date = Column(Date, nullable=False)
    mileage_at_service = Column(Integer, nullable=False)
    cost = Column(Numeric(8, 2))
    performed_by = Column(Text)
    notes = Column(Text)
    receipt_key = Column(Text)