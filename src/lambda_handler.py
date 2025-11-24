import json
from typing import Any, Dict

from .event_router import identify_event_type
from .remediation import run_remediation
from src.remediation.ec2_status_check import extract_instance_id


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    print("=== Incoming Event ===")
    print(json.dumps(event, indent=2, ensure_ascii=False))

    parsed_event = {"raw": event, "instance_id": extract_instance_id(event)}

    event_type = identify_event_type(event)
    print("Identified event type: " + str(event_type))

    remediation_result = run_remediation(event_type, parsed_event)
    print(
        "Remediation result: ",
        json.dumps(remediation_result, indent=2, ensure_ascii=False),
    )

    response_body = {
        "event_type": event_type,
        "remediation": remediation_result,
    }

    return {"statusCode": 200, "body": json.dumps(response_body)}
