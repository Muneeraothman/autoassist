from datetime import date, datetime, timezone

from engine import get_upcoming_maintenance
from models import ScheduleItem, ServiceRecord, Vehicle


def make_vehicle(current_mileage, avg_miles_per_day, mileage_updated_at):
    return Vehicle(
        id=1,
        make="Lexus",
        model="ES300",
        year=2002,
        current_mileage=current_mileage,
        mileage_updated_at=mileage_updated_at,
        avg_miles_per_day=avg_miles_per_day,
    )


def test_mileage_trigger_wins_for_heavy_driver():
    item = ScheduleItem(id=1, vehicle_id=1, service_name="Oil change",
                         interval_miles=5000, interval_months=6)
    last_service = ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                                  service_date=date(2026, 6, 1), mileage_at_service=95000)
    vehicle = make_vehicle(current_mileage=99500, avg_miles_per_day=50,
                            mileage_updated_at=datetime(2026, 7, 10, tzinfo=timezone.utc))
    today = date(2026, 7, 15)

    [result] = get_upcoming_maintenance(vehicle, [item], [last_service], today)

    assert result["due_date"] == date(2026, 7, 20)
    assert result["due_miles"] == 100000
    assert result["status"] == "DUE_SOON"


def test_time_trigger_wins_for_light_driver():
    item = ScheduleItem(id=1, vehicle_id=1, service_name="Oil change",
                         interval_miles=5000, interval_months=6)
    last_service = ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                                  service_date=date(2026, 1, 15), mileage_at_service=90000)
    vehicle = make_vehicle(current_mileage=90100, avg_miles_per_day=5,
                            mileage_updated_at=datetime(2026, 7, 1, tzinfo=timezone.utc))
    today = date(2026, 7, 10)

    [result] = get_upcoming_maintenance(vehicle, [item], [last_service], today)

    assert result["due_date"] == date(2026, 7, 15)
    assert result["status"] == "DUE_SOON"


def test_time_only_item_skips_mileage_projection():
    item = ScheduleItem(id=1, vehicle_id=1, service_name="Brake fluid",
                         interval_miles=None, interval_months=6)
    last_service = ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                                  service_date=date(2026, 3, 1), mileage_at_service=88000)
    vehicle = make_vehicle(current_mileage=90000, avg_miles_per_day=30,
                            mileage_updated_at=datetime(2026, 7, 1, tzinfo=timezone.utc))
    today = date(2026, 7, 15)

    [result] = get_upcoming_maintenance(vehicle, [item], [last_service], today)

    assert result["due_date"] == date(2026, 9, 1)
    assert result["due_miles"] is None
    assert result["miles_remaining"] is None
    assert result["status"] == "OK"


def test_never_serviced_item_is_overdue():
    item = ScheduleItem(id=1, vehicle_id=1, service_name="Timing belt",
                         interval_miles=90000, interval_months=84)
    vehicle = make_vehicle(current_mileage=90000, avg_miles_per_day=30,
                            mileage_updated_at=datetime(2026, 7, 1, tzinfo=timezone.utc))
    today = date(2026, 7, 15)

    [result] = get_upcoming_maintenance(vehicle, [item], [], today)

    assert result["status"] == "OVERDUE"
    assert result["due_date"] is None
    assert result["due_miles"] is None
    assert result["days_remaining"] is None
    assert result["miles_remaining"] is None


def test_serviced_item_overdue_when_time_trigger_already_passed():
    item = ScheduleItem(id=1, vehicle_id=1, service_name="Oil change",
                         interval_miles=5000, interval_months=6)
    last_service = ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                                  service_date=date(2025, 1, 1), mileage_at_service=80000)
    vehicle = make_vehicle(current_mileage=80100, avg_miles_per_day=1,
                            mileage_updated_at=datetime(2025, 1, 1, tzinfo=timezone.utc))
    today = date(2026, 7, 15)

    [result] = get_upcoming_maintenance(vehicle, [item], [last_service], today)

    assert result["due_date"] == date(2025, 7, 1)
    assert result["status"] == "OVERDUE"


def test_due_soon_triggered_by_miles_threshold_alone():
    # Mileage-only item, light driver: 100 miles remain (well under the 500-mile
    # threshold) but that projects out 50 days (over the 30-day threshold).
    # This only passes because the bucketing checks miles_remaining independently
    # of days_remaining, per the build guide's "within 30 days OR 500 miles" spec.
    item = ScheduleItem(id=1, vehicle_id=1, service_name="Oil change",
                         interval_miles=5000, interval_months=None)
    last_service = ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                                  service_date=date(2026, 1, 1), mileage_at_service=94800)
    vehicle = make_vehicle(current_mileage=99700, avg_miles_per_day=2,
                            mileage_updated_at=datetime(2026, 7, 15, tzinfo=timezone.utc))
    today = date(2026, 7, 15)

    [result] = get_upcoming_maintenance(vehicle, [item], [last_service], today)

    assert result["miles_remaining"] == 100
    assert result["days_remaining"] == 50
    assert result["status"] == "DUE_SOON"


def test_zero_avg_miles_per_day_skips_mileage_projection():
    item = ScheduleItem(id=1, vehicle_id=1, service_name="Oil change",
                         interval_miles=5000, interval_months=6)
    last_service = ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                                  service_date=date(2026, 1, 1), mileage_at_service=90000)
    vehicle = make_vehicle(current_mileage=90000, avg_miles_per_day=0,
                            mileage_updated_at=datetime(2026, 7, 1, tzinfo=timezone.utc))
    today = date(2026, 7, 15)

    [result] = get_upcoming_maintenance(vehicle, [item], [last_service], today)

    assert result["due_miles"] is None
    assert result["miles_remaining"] is None
    assert result["due_date"] == date(2026, 7, 1)  # falls back to the time trigger


def test_item_with_no_intervals_has_no_projection():
    item = ScheduleItem(id=1, vehicle_id=1, service_name="Misc inspection",
                         interval_miles=None, interval_months=None)
    last_service = ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                                  service_date=date(2026, 1, 1), mileage_at_service=90000)
    vehicle = make_vehicle(current_mileage=90000, avg_miles_per_day=30,
                            mileage_updated_at=datetime(2026, 7, 1, tzinfo=timezone.utc))
    today = date(2026, 7, 15)

    [result] = get_upcoming_maintenance(vehicle, [item], [last_service], today)

    assert result["due_date"] is None
    assert result["status"] == "OK"


def test_DELIBERATELY_BROKEN_for_phase8_checkpoint():
    # Intentional, temporary failure to verify CD blocks deployment on a
    # failing test. Will be removed immediately after the checkpoint.
    assert 1 == 2
