# src/remediation/ec2_high_cpu.py
from typing import Any, Dict


def handle(event: Dict[str, Any]) -> Dict[str, Any]:

    print("[Remediation] Handling EC2 high CPU alarm")

    return {
        "remediation_type": "EC2_HIGH_CPU",
        "action": "NOOP",
        "message": "Simulated handling for EC2 high CPU alarm",
    }
