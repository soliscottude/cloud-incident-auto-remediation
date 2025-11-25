import os
from typing import Any, Dict
from src.utils.aws_clients import get_ec2_client


DRY_RUN_ONLY = os.getenv("DRY_RUN_ONLY", "true").lower() == "true"


def handle(parsed_event: Dict[str, Any]) -> Dict[str, Any]:

    print("[Remediation] StatusCheckFailed remediation started")

    instance_id = parsed_event.get("instance_id")

    if not instance_id:
        print("[Remediation] No instance ID found.")
        return {
            "remediation_type": "EC2_STATUS_CHECK_FAILED",
            "action": "SKIP",
            "message": "No instance ID found in event",
        }

    # get EC2 client
    ec2 = get_ec2_client()

    # 执行重启前打印安全日志
    print("[Remediation] Attempting to reboot instance:", instance_id)

    try:
        # ⭐ 安全保护：DryRun 先尝试，如果没权限 / 无效会抛 DryRunOperation
        ec2.reboot_instances(InstanceIds=[instance_id], DryRun=True)
    except Exception as e:
        if "DryRunOperation" not in str(e):
            print("[Remediation] DryRun failed:", str(e))
            return {
                "remediation_type": "EC2_STATUS_CHECK_FAILED",
                "action": "FAILED_DRY_RUN",
                "message": str(e),
            }

    if DRY_RUN_ONLY:
        print("[Remediation] DRY_RUN_ONLY=true, skip real reboot.")
        return {
            "remediation_type": "EC2_STATUS_CHECK_FAILED",
            "instance_id": instance_id,
            "action": "WOULD_REBOOT",
            "message": "DryRun succeeded; real reboot skipped because DRY_RUN_ONLY=true",
        }

    # ⭐ DryRun 成功，说明权限OK，可以安全执行重启
    ec2.reboot_instances(InstanceIds=[instance_id], DryRun=False)

    print("[Remediation] Reboot executed for:", instance_id)

    return {
        "remediation_type": "EC2_STATUS_CHECK_FAILED",
        "instance_id": instance_id,
        "action": "REBOOT",
        "message": "EC2 instance rebooted due to StatusCheckFailed",
    }
