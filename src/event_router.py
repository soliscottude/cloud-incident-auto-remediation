from typing import Any, Dict


def identify_event_type(event: Dict[str, Any]) -> str:
    detail = event.get("detail", {})
    alarm_name = str(detail.get("alarmName", "")).lower()

    if "cpu" in alarm_name:
        return "EC2_HIGH_CPU"

    if "status" in alarm_name:
        return "EC2_STATUS_CHECK_FAILED"

    if "stop" in alarm_name:
        return "EC2_UNEXPECTED_STOP"

    return "UNKNOWN"
