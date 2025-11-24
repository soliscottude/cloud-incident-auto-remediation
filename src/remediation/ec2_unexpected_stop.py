# src/remediation/ec2_unexpected_stop.py
from typing import Any, Dict


def handle(event: Dict[str, Any]) -> Dict[str, Any]:

    print("[Remediation] Handling EC2 unexpected stop")

    return {
        "remediation_type": "EC2_UNEXPECTED_STOP",
        "action": "NOOP",
        "message": "Simulated handling for EC2 unexpected stop",
    }
