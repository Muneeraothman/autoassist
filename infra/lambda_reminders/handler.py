"""Daily maintenance reminder emails.

Deliberately thin: all business logic (what's due, dedup against
notifications_log) lives in the backend, called over plain HTTPS via a
shared-secret-protected internal endpoint rather than direct RDS access.
Two reasons, not just one: (1) the backend's engine.py logic is already
tested and used by the real app, no reason to duplicate it here, and
(2) RDS is in private subnets, so direct access would require this Lambda
to be VPC-attached, which would then need a NAT gateway or SES VPC
endpoint to reach anything on the public internet at all -- an ongoing
cost this project deliberately avoided in Phase 7 by not provisioning
a NAT gateway. Staying outside the VPC sidesteps that entirely.

The backend's own public IP changes every destroy/apply cycle (Phase 7's
standing destroy-between-sessions pattern), so it can't be hardcoded --
read from SSM Parameter Store, where user_data.sh.tpl writes it at boot.
"""

import json
import os
import urllib.error
import urllib.request
from collections import defaultdict

import boto3

BACKEND_URL_PARAM = os.environ["BACKEND_URL_PARAM"]
INTERNAL_API_KEY = os.environ["INTERNAL_API_KEY"]
SES_SENDER_EMAIL = os.environ["SES_SENDER_EMAIL"]
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

ssm = boto3.client("ssm", region_name=AWS_REGION)
ses = boto3.client("ses", region_name=AWS_REGION)


def _get_backend_url():
    response = ssm.get_parameter(Name=BACKEND_URL_PARAM)
    return response["Parameter"]["Value"]


def _call_backend(method, path, body=None):
    url = f"{_get_backend_url()}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "X-Internal-Api-Key": INTERNAL_API_KEY,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _format_email(vehicle_label, items):
    text_lines = []
    html_lines = []
    for item in items:
        if item["status"] == "OVERDUE":
            due_text = f"OVERDUE - was due {item['due_date'] or 'previously'}"
        else:
            parts = []
            if item["due_date"]:
                parts.append(f"by {item['due_date']}")
            if item["miles_remaining"] is not None:
                parts.append(f"in ~{round(item['miles_remaining'])} mi")
            due_text = "Due soon" + (f" ({', '.join(parts)})" if parts else "")
        text_lines.append(f"- {item['service_name']}: {due_text}")
        html_lines.append(f"<li><strong>{item['service_name']}</strong>: {due_text}</li>")

    subject = f"AutoAssist: {len(items)} maintenance item(s) due for your {vehicle_label}"
    text_body = f"Your {vehicle_label} has upcoming maintenance:\n\n" + "\n".join(text_lines)
    html_body = f"""
    <html>
      <body style="font-family: sans-serif;">
        <h2>Maintenance due for your {vehicle_label}</h2>
        <ul>{''.join(html_lines)}</ul>
      </body>
    </html>
    """
    return subject, text_body, html_body


def handler(event, context):
    try:
        due_items = _call_backend("GET", "/api/internal/reminders-due")
    except (urllib.error.URLError, TimeoutError) as e:
        # Expected, not an error: the app is only up while Terraform infra
        # is actually applied (destroy-between-sessions). Same "skip
        # gracefully" treatment as Phase 8's CD deploy step.
        print(f"Backend unreachable (infra likely torn down for the session): {e}")
        return {"skipped": True, "reason": "backend unreachable"}

    by_vehicle = defaultdict(list)
    for item in due_items:
        key = (item["user_id"], item["user_email"], item["vehicle_id"], item["vehicle_label"])
        by_vehicle[key].append(item)

    sent_notifications = []
    emails_sent = 0

    for (user_id, user_email, vehicle_id, vehicle_label), items in by_vehicle.items():
        subject, text_body, html_body = _format_email(vehicle_label, items)
        try:
            ses.send_email(
                Source=SES_SENDER_EMAIL,
                Destination={"ToAddresses": [user_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": text_body}, "Html": {"Data": html_body}},
                },
            )
        except Exception as e:
            print(f"Failed to send email to {user_email}: {e}")
            continue

        emails_sent += 1
        for item in items:
            sent_notifications.append(
                {
                    "user_id": user_id,
                    "vehicle_id": vehicle_id,
                    "schedule_item_id": item["schedule_item_id"],
                }
            )

    if sent_notifications:
        _call_backend("POST", "/api/internal/reminders-sent", {"notifications": sent_notifications})

    print(f"Sent {emails_sent} reminder email(s), recorded {len(sent_notifications)} notification(s)")
    return {"emails_sent": emails_sent, "notifications_recorded": len(sent_notifications)}
