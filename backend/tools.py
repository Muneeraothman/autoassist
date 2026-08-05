from datetime import date

from embeddings import embed_text
from engine import get_upcoming_maintenance
from models import ManualChunk, ScheduleItem, ServiceRecord, Vehicle
from stats import OTHER_CATEGORY, compute_stats

MANUAL_SEARCH_RESULTS_LIMIT = 5


class ToolError(Exception):
    pass


TOOL_SPECS = [
    {
        "toolSpec": {
            "name": "get_vehicle_info",
            "description": "Get basic info about one of the user's vehicles: make, model, year, current mileage, and average miles driven per day.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "vehicle_id": {"type": "integer", "description": "The vehicle's id"},
                    },
                    "required": ["vehicle_id"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "get_upcoming_maintenance",
            "description": "Get upcoming/overdue maintenance items for one of the user's vehicles - status (OVERDUE, DUE_SOON, OK), due date, and miles/days remaining for each scheduled service.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "vehicle_id": {"type": "integer", "description": "The vehicle's id"},
                    },
                    "required": ["vehicle_id"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "get_service_history",
            "description": "Get past service records for one of the user's vehicles, newest first. Optionally filter by service name (partial match) or a start date.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "vehicle_id": {"type": "integer", "description": "The vehicle's id"},
                        "service_name": {
                            "type": "string",
                            "description": "Optional partial service name to filter by, e.g. 'oil'",
                        },
                        "since_date": {
                            "type": "string",
                            "description": "Optional ISO date (YYYY-MM-DD) - only return records on/after this date",
                        },
                    },
                    "required": ["vehicle_id"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "get_spending_summary",
            "description": "Get spending totals for one of the user's vehicles: total spend, cost per mile, breakdown by service category, breakdown by year. Optionally scope to one year or filter to one category.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "vehicle_id": {"type": "integer", "description": "The vehicle's id"},
                        "category": {
                            "type": "string",
                            "description": "Optional partial category name to filter by, e.g. 'oil'",
                        },
                        "year": {"type": "integer", "description": "Optional year to scope spending to"},
                    },
                    "required": ["vehicle_id"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "search_manual",
            "description": "Search the vehicle's owner's manual and maintenance guide for information like fluid types/capacities, part specifications, or how-to procedures - anything that lives in the manual text rather than the structured maintenance schedule. Returns excerpts with page numbers; always cite the page number when answering from this tool's results. Do not use this for questions about what's due, service history, or spending - use the other tools for those.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "What to search for in the manual"},
                        "vehicle_id": {"type": "integer", "description": "The vehicle's id"},
                    },
                    "required": ["query", "vehicle_id"],
                }
            },
        }
    },
]


def _get_owned_vehicle(db, current_user, vehicle_id) -> Vehicle:
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle is None or vehicle.user_id != current_user.id:
        raise ToolError(f"No vehicle with id {vehicle_id} found for this user.")
    return vehicle


def _tool_get_vehicle_info(db, current_user, vehicle_id, **_kwargs):
    vehicle = _get_owned_vehicle(db, current_user, vehicle_id)
    return {
        "id": vehicle.id,
        "make": vehicle.make,
        "model": vehicle.model,
        "year": vehicle.year,
        "current_mileage": vehicle.current_mileage,
        "avg_miles_per_day": float(vehicle.avg_miles_per_day),
    }


def _tool_get_upcoming_maintenance(db, current_user, vehicle_id, **_kwargs):
    vehicle = _get_owned_vehicle(db, current_user, vehicle_id)
    schedule_items = db.query(ScheduleItem).filter(ScheduleItem.vehicle_id == vehicle_id).all()
    service_records = db.query(ServiceRecord).filter(ServiceRecord.vehicle_id == vehicle_id).all()

    results = get_upcoming_maintenance(vehicle, schedule_items, service_records, date.today())

    return [
        {
            "service_name": entry["schedule_item"].service_name,
            "status": entry["status"],
            "due_date": str(entry["due_date"]) if entry["due_date"] else None,
            "days_remaining": entry["days_remaining"],
            "miles_remaining": entry["miles_remaining"],
        }
        for entry in results
    ]


def _tool_get_service_history(db, current_user, vehicle_id, service_name=None, since_date=None, **_kwargs):
    _get_owned_vehicle(db, current_user, vehicle_id)
    schedule_names = {
        item.id: item.service_name
        for item in db.query(ScheduleItem).filter(ScheduleItem.vehicle_id == vehicle_id).all()
    }

    query = db.query(ServiceRecord).filter(ServiceRecord.vehicle_id == vehicle_id)
    if since_date:
        try:
            parsed_date = date.fromisoformat(since_date)
        except ValueError:
            raise ToolError(f"Invalid since_date '{since_date}', expected YYYY-MM-DD.")
        query = query.filter(ServiceRecord.service_date >= parsed_date)

    records = query.order_by(ServiceRecord.service_date.desc()).all()

    if service_name:
        matching_ids = {
            item_id for item_id, name in schedule_names.items() if service_name.lower() in name.lower()
        }
        records = [r for r in records if r.schedule_item_id in matching_ids]

    return [
        {
            "service_name": schedule_names.get(r.schedule_item_id, OTHER_CATEGORY),
            "service_date": str(r.service_date),
            "mileage_at_service": r.mileage_at_service,
            "cost": float(r.cost) if r.cost is not None else None,
            "performed_by": r.performed_by,
            "notes": r.notes,
        }
        for r in records
    ]


def _tool_get_spending_summary(db, current_user, vehicle_id, category=None, year=None, **_kwargs):
    vehicle = _get_owned_vehicle(db, current_user, vehicle_id)
    schedule_items = db.query(ScheduleItem).filter(ScheduleItem.vehicle_id == vehicle_id).all()
    service_records = db.query(ServiceRecord).filter(ServiceRecord.vehicle_id == vehicle_id).all()

    if year is not None:
        service_records = [r for r in service_records if r.service_date.year == year]

    result = compute_stats(vehicle, schedule_items, service_records)

    if category:
        result["spend_by_category"] = [
            entry for entry in result["spend_by_category"] if category.lower() in entry["category"].lower()
        ]

    return result


def _tool_search_manual(db, current_user, query, vehicle_id, **_kwargs):
    _get_owned_vehicle(db, current_user, vehicle_id)
    query_embedding = embed_text(query)

    results = (
        db.query(ManualChunk)
        .filter(ManualChunk.vehicle_id == vehicle_id)
        .order_by(ManualChunk.embedding.cosine_distance(query_embedding))
        .limit(MANUAL_SEARCH_RESULTS_LIMIT)
        .all()
    )

    if not results:
        return {"results": [], "note": "No manual has been ingested for this vehicle yet."}

    return {
        "results": [
            {
                "source_file": r.source_file,
                "page_number": r.page_number,
                "excerpt": r.chunk_text,
            }
            for r in results
        ]
    }


TOOL_FUNCTIONS = {
    "get_vehicle_info": _tool_get_vehicle_info,
    "get_upcoming_maintenance": _tool_get_upcoming_maintenance,
    "get_service_history": _tool_get_service_history,
    "get_spending_summary": _tool_get_spending_summary,
    "search_manual": _tool_search_manual,
}


def execute_tool(name, tool_input, db, current_user):
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        raise ToolError(f"Unknown tool: {name}")
    return func(db, current_user, **tool_input)
