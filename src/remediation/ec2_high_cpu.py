import logging
from typing import Any, Dict


def handle(parsed_event: Dict[str, Any]) -> Dict[str, Any]:
    print("[Remediation] High CPU remediation started")

    instance_id = parsed_event.get("instance_id")

    return {
        "remediation_type": "EC2_HIGH_CPU",
        "instance_id": instance_id,
        "action": "NO_ACTION",
        "message": "High CPU alarm received for instance "
        + str(instance_id)
        + ". No auto-scaling configured.",
    }
