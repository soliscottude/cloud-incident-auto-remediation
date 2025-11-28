import json
from typing import Any, Dict

from .event_router import identify_event_type, extract_instance_id
from .remediation import run_remediation
from .storage.dynamodb_client import put_incident
from .utils.logging_utils import get_logger, log_json

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main entry point for the Auto-Remediation Lambda.

    Steps performed:
    1. Log the incoming CloudWatch/SNS event.
    2. Extract instance_id or related resource ID.
    3. Identify the event type (StatusCheckFailed, HighCPU, UnexpectedStop, etc.).
    4. Run the corresponding remediation action.
    5. Store incident details in DynamoDB.
    6. Return a structured response.
    """

    # Step 1 — Log the raw incoming event
    log_json(
        logger,
        "info",
        "Incoming CloudWatch/SNS event (deployed-v2)",
        {"step": 1, "event": event},
    )

    # Step 2 — Extract instance ID from the event payload
    instance_id = extract_instance_id(event)
    parsed_event = {
        "raw": event,
        "instance_id": instance_id,
    }
    log_json(
        logger,
        "info",
        "Extracted instance ID",
        {"step": 2, "instance_id": instance_id},
    )

    # Step 3 — Determine which remediation rule should be triggered
    event_type = identify_event_type(event)
    log_json(
        logger,
        "info",
        "Identified event type",
        {"step": 3, "event_type": str(event_type)},
    )

    # Step 4 — Execute remediation logic based on event type
    remediation_result = run_remediation(event_type, parsed_event)
    log_json(
        logger,
        "info",
        "Remediation executed",
        {
            "step": 4,
            "event_type": str(event_type),
            "remediation_result": remediation_result,
        },
    )

    # Step 5 — Persist incident result into DynamoDB
    saved_item = put_incident(
        event_type=event_type,
        instance_id=parsed_event.get("instance_id"),
        remediation=remediation_result,
        raw_event=parsed_event.get("raw"),
    )
    log_json(
        logger,
        "info",
        "Incident stored in DynamoDB",
        {"step": 5, "saved_item": saved_item},
    )

    # Step 6 — Construct API/Lambda response
    response_body = {
        "event_type": str(event_type),
        "remediation": remediation_result,
    }

    log_json(
        logger,
        "info",
        "Lambda execution completed successfully",
        {"step": 6, "response_body": response_body},
    )

    return {
        "statusCode": 200,
        "body": json.dumps(response_body),
    }


if __name__ == "__main__":
    # Minimal local test harness for manual runs like:
    # python3 -m src.lambda_handler

    # You can replace this with a real CloudWatch Alarm sample event later.
    test_event: Dict[str, Any] = {}

    result = lambda_handler(test_event, context=None)
    print("Local test invocation result:")
    print(json.dumps(result, indent=2))
