OTHER_CATEGORY = "Other / Unscheduled Repair"


def compute_stats(vehicle, schedule_items, service_records):
    schedule_names = {item.id: item.service_name for item in schedule_items}

    total_spend = 0.0
    by_category = {}
    by_year = {}
    earliest_record = None

    for record in service_records:
        cost = float(record.cost) if record.cost is not None else 0.0
        total_spend += cost

        category = schedule_names.get(record.schedule_item_id, OTHER_CATEGORY)
        by_category[category] = by_category.get(category, 0.0) + cost

        year = record.service_date.year
        by_year[year] = by_year.get(year, 0.0) + cost

        if earliest_record is None or record.service_date < earliest_record.service_date:
            earliest_record = record

    spend_by_category = sorted(
        [{"category": category, "total": round(total, 2)} for category, total in by_category.items()],
        key=lambda entry: entry["total"],
        reverse=True,
    )
    spend_by_year = sorted(
        [{"year": year, "total": round(total, 2)} for year, total in by_year.items()],
        key=lambda entry: entry["year"],
    )

    cost_per_mile = None
    if earliest_record is not None:
        miles_driven = vehicle.current_mileage - earliest_record.mileage_at_service
        if miles_driven > 0:
            cost_per_mile = round(total_spend / miles_driven, 4)

    return {
        "total_spend": round(total_spend, 2),
        "cost_per_mile": cost_per_mile,
        "spend_by_category": spend_by_category,
        "spend_by_year": spend_by_year,
    }
