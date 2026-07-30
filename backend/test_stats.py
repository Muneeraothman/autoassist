from datetime import date

from models import ScheduleItem, ServiceRecord, Vehicle
from stats import OTHER_CATEGORY, compute_stats


def make_vehicle(current_mileage):
    return Vehicle(id=1, make="Lexus", model="ES300", year=2002, current_mileage=current_mileage)


def test_total_spend_sums_all_records_treating_null_cost_as_zero():
    items = [ScheduleItem(id=1, vehicle_id=1, service_name="Oil change")]
    records = [
        ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                      service_date=date(2025, 1, 1), mileage_at_service=10000, cost=50.00),
        ServiceRecord(id=2, vehicle_id=1, schedule_item_id=1,
                      service_date=date(2025, 6, 1), mileage_at_service=15000, cost=None),
    ]

    result = compute_stats(make_vehicle(20000), items, records)

    assert result["total_spend"] == 50.00


def test_spend_by_category_groups_by_schedule_item_and_buckets_unscheduled_repairs():
    items = [
        ScheduleItem(id=1, vehicle_id=1, service_name="Oil change"),
        ScheduleItem(id=2, vehicle_id=1, service_name="Tire rotation"),
    ]
    records = [
        ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                      service_date=date(2025, 1, 1), mileage_at_service=10000, cost=50.00),
        ServiceRecord(id=2, vehicle_id=1, schedule_item_id=1,
                      service_date=date(2025, 6, 1), mileage_at_service=15000, cost=60.00),
        ServiceRecord(id=3, vehicle_id=1, schedule_item_id=2,
                      service_date=date(2025, 3, 1), mileage_at_service=12000, cost=30.00),
        ServiceRecord(id=4, vehicle_id=1, schedule_item_id=None,
                      service_date=date(2025, 4, 1), mileage_at_service=13000, cost=200.00),
    ]

    result = compute_stats(make_vehicle(20000), items, records)

    # Sorted by total descending: the "Other" bucket (200) outranks "Oil change" (110).
    assert result["spend_by_category"] == [
        {"category": OTHER_CATEGORY, "total": 200.00},
        {"category": "Oil change", "total": 110.00},
        {"category": "Tire rotation", "total": 30.00},
    ]


def test_spend_by_year_groups_and_sorts_ascending():
    items = [ScheduleItem(id=1, vehicle_id=1, service_name="Oil change")]
    records = [
        ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                      service_date=date(2026, 1, 1), mileage_at_service=20000, cost=40.00),
        ServiceRecord(id=2, vehicle_id=1, schedule_item_id=1,
                      service_date=date(2024, 6, 1), mileage_at_service=10000, cost=50.00),
        ServiceRecord(id=3, vehicle_id=1, schedule_item_id=1,
                      service_date=date(2024, 12, 1), mileage_at_service=12000, cost=25.00),
    ]

    result = compute_stats(make_vehicle(25000), items, records)

    assert result["spend_by_year"] == [
        {"year": 2024, "total": 75.00},
        {"year": 2026, "total": 40.00},
    ]


def test_cost_per_mile_uses_earliest_record_as_baseline():
    items = [ScheduleItem(id=1, vehicle_id=1, service_name="Oil change")]
    records = [
        ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                      service_date=date(2025, 6, 1), mileage_at_service=15000, cost=60.00),
        ServiceRecord(id=2, vehicle_id=1, schedule_item_id=1,
                      service_date=date(2025, 1, 1), mileage_at_service=10000, cost=50.00),
    ]

    result = compute_stats(make_vehicle(20000), items, records)

    # baseline mileage is 10000 (the earliest record by date), not 15000
    assert result["cost_per_mile"] == round(110.00 / 10000, 4)


def test_cost_per_mile_is_none_with_no_service_records():
    items = [ScheduleItem(id=1, vehicle_id=1, service_name="Oil change")]

    result = compute_stats(make_vehicle(20000), items, [])

    assert result["cost_per_mile"] is None
    assert result["total_spend"] == 0.0
    assert result["spend_by_category"] == []
    assert result["spend_by_year"] == []


def test_cost_per_mile_is_none_when_no_miles_have_accumulated():
    items = [ScheduleItem(id=1, vehicle_id=1, service_name="Oil change")]
    records = [
        ServiceRecord(id=1, vehicle_id=1, schedule_item_id=1,
                      service_date=date(2025, 1, 1), mileage_at_service=20000, cost=50.00),
    ]

    result = compute_stats(make_vehicle(20000), items, records)

    assert result["cost_per_mile"] is None
