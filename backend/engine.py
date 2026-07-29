from datetime import timedelta

from dateutil.relativedelta import relativedelta

DUE_SOON_DAYS = 30
DUE_SOON_MILES = 500


def get_upcoming_maintenance(vehicle, schedule_items, service_records, today,
                              due_soon_days=DUE_SOON_DAYS, due_soon_miles=DUE_SOON_MILES):
    results = []

    for item in schedule_items:
        matching_records = [r for r in service_records if r.schedule_item_id == item.id]

        if not matching_records:
            results.append({
                "schedule_item": item,
                "due_date": None,
                "due_miles": None,
                "status": "OVERDUE",
                "days_remaining": None,
                "miles_remaining": None,
            })
            continue

        last_record = max(matching_records, key=lambda r: r.service_date)

        due_at_miles = None
        miles_remaining = None
        mileage_due_date = None
        avg_miles_per_day = float(vehicle.avg_miles_per_day)
        if item.interval_miles is not None and avg_miles_per_day > 0:
            due_at_miles = last_record.mileage_at_service + item.interval_miles
            days_since_update = (today - vehicle.mileage_updated_at.date()).days
            estimated_current_mileage = vehicle.current_mileage + avg_miles_per_day * days_since_update
            miles_remaining = due_at_miles - estimated_current_mileage
            days_until_due = miles_remaining / avg_miles_per_day
            mileage_due_date = today + timedelta(days=days_until_due)

        time_due_date = None
        if item.interval_months is not None:
            time_due_date = last_record.service_date + relativedelta(months=item.interval_months)

        candidates = [d for d in [mileage_due_date, time_due_date] if d is not None]
        if not candidates:
            due_date = None
            days_remaining = None
            status = "OK"
        else:
            due_date = min(candidates)
            days_remaining = (due_date - today).days
            if due_date < today:
                status = "OVERDUE"
            elif days_remaining <= due_soon_days or (
                miles_remaining is not None and miles_remaining <= due_soon_miles
            ):
                status = "DUE_SOON"
            else:
                status = "OK"

        results.append({
            "schedule_item": item,
            "due_date": due_date,
            "due_miles": due_at_miles,
            "status": status,
            "days_remaining": days_remaining,
            "miles_remaining": miles_remaining,
        })

    return results
