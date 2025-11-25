import os
import uuid
import datetime
from typing import Any, Dict

import boto3


def get_table():
    table_name = os.environ.get("INCIDENT_TABLE_NAME", "incident_events")
    print("[DEBUG] Using DynamoDB table: " + str(table_name) + " | Step 5: table name")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    return table


def put_incident(
    event_type: str,
    instance_id: str,
    remediation: Dict[str, Any],
    raw_event: Dict[str, Any],
) -> Dict[str, Any]:
    table = get_table()

    now = datetime.datetime.utcnow().isoformat() + "Z"
    incident_id = str(uuid.uuid4())

    item = {
        "pk": "INCIDENT#" + str(event_type),
        "sk": now + "#" + incident_id,
        "event_type": event_type,
        "instance_id": instance_id,
        "remediation_type": remediation.get("remediation_type"),
        "action": remediation.get("action"),
        "message": remediation.get("message"),
        "created_at": now,
        "raw_event": raw_event,
    }

    table.put_item(Item=item)
    return item
