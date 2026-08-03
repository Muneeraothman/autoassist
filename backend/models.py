from sqlalchemy import Boolean, Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    hashed_password = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    email_verified = Column(Boolean, nullable=False, default=False)


class EmailToken(Base):
    __tablename__ = "email_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(Text, nullable=False, unique=True)
    token_type = Column(Text, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
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