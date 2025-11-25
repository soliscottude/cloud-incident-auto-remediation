import json
from typing import Any, Dict

from .event_router import identify_event_type, extract_instance_id
from .remediation import run_remediation
from .storage.dynamodb_client import put_incident


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    print("=== Incoming Event === (Step 1: get incident json)")
    print(json.dumps(event, indent=2, ensure_ascii=False))

    parsed_event = {"raw": event, "instance_id": extract_instance_id(event)}
    print(
        "Identified instance ID: "
        + parsed_event["instance_id"]
        + " | Step 2: get instance ID of the incident"
    )

    event_type = identify_event_type(event)
    print("Identified event type: " + str(event_type) + " | Step 3: get incident type")

    remediation_result = run_remediation(event_type, parsed_event)
    print(
        "Remediation result: ",
        json.dumps(remediation_result, indent=2, ensure_ascii=False),
        " | Step 4: run remediation",
    )

    saved_item = put_incident(
        event_type=event_type,
        instance_id=parsed_event.get("instance_id"),
        remediation=remediation_result,
        raw_event=parsed_event.get("raw"),
    )
    print(
        "[DynamoDB] Saved incident item: ",
        json.dumps(saved_item, indent=2, ensure_ascii=False),
        " | Step 6: save item to table",
    )

    response_body = {
        "event_type": event_type,
        "remediation": remediation_result,
    }

    return {"statusCode": 200, "body": json.dumps(response_body)}
