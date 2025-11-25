from typing import Any, Dict


def extract_instance_id(event):
    try:
        metrics = event.get("detail", {}).get("configuration", {}).get("metrics", [])

        if not metrics:
            return None

        dimensions = (
            metrics[0].get("metricStat", {}).get("metric", {}).get("dimensions", [])
        )

        for d in dimensions:
            if d.get("name") == "InstanceId":
                return d.get("value")

        return None

    except Exception:
        return None


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
