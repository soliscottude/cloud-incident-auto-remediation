from typing import Any, Dict

from . import ec2_high_cpu
from . import ec2_status_check
from . import ec2_unexpected_stop


def run_remediation(event_type: str, parsed_event: Dict[str, Any]) -> Dict[str, Any]:

    if event_type == "EC2_HIGH_CPU":

        return ec2_high_cpu.handle(parsed_event)

    if event_type == "EC2_STATUS_CHECK_FAILED":

        return ec2_status_check.handle(parsed_event)

    if event_type == "EC2_UNEXPECTED_STOP":

        return ec2_unexpected_stop.handle(parsed_event)

    print("[Remediation] No remediation rule for event type:", event_type)
    return {
        "remediation_type": "UNKNOWN",
        "action": "SKIP",
        "message": "No remediation implemented for event type: " + event_type,
    }
