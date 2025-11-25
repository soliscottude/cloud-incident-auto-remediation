import logging
from typing import Dict, Any
from ..utils.aws_clients import get_ec2_client


def handle(parsed_event: Dict[str, Any]) -> Dict[str, Any]:
    print("[Remediation] Unexpected Stop remediation started")

    instance_id = parsed_event.get("instance_id")
    ec2 = get_ec2_client()

    try:
        print("[DryRun] Attempting to start instance: " + str(instance_id))

        ec2.start_instances(InstanceIds=[instance_id], DryRun=True)

        return {
            "remediation_type": "EC2_UNEXPECTED_STOP",
            "instance_id": instance_id,
            "action": "START_INSTANCE",
            "message": "DryRun success: instance "
            + str(instance_id)
            + " would be started",
        }

    except Exception as e:
        return {
            "remediation_type": "EC2_UNEXPECTED_STOP",
            "instance_id": instance_id,
            "action": "FAILED",
            "message": str(e),
        }
