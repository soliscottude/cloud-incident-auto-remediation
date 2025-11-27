import datetime
from collections import Counter
from typing import List, Dict


def build_markdown_report(date_str: str, incidents: List[Dict]) -> str:
    # 统计
    total_incidents = len(incidents)
    success = sum(1 for x in incidents if x.get("success", False))
    failed = total_incidents - success
    unique_instances = len({x["instance_id"] for x in incidents})

    by_event = Counter(x["event_type"] for x in incidents)
    by_remediation = Counter(x["remediation_type"] for x in incidents)

    lines = []

    lines.append(f"# Daily Cloud Incident Report - {date_str}")
    lines.append("")
    lines.append("**Summary**")
    lines.append(f"- Total incidents: {total_incidents}")
    lines.append(f"- Success (heuristic): {success}")
    lines.append(f"- Failed (heuristic): {failed}")
    lines.append(f"- Unique instances: {unique_instances}")
    lines.append("")
    lines.append("**By event type**")
    for k, v in by_event.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("**By remediation type**")
    for k, v in by_remediation.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Incident Details")
    lines.append("")
    lines.append(
        "| Time (created_at) | Event Type | Instance ID | Remediation Type | Action | Message |"
    )
    lines.append(
        "|-------------------|-----------|-------------|------------------|--------|---------|"
    )

    for inc in incidents:
        lines.append(
            f"| {inc['created_at']} "
            f"| {inc['event_type']} "
            f"| {inc['instance_id']} "
            f"| {inc['remediation_type']} "
            f"| {inc['action']} "
            f"| {inc['message']} |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    # 想生成哪一天的日报就改这里
    date_str = "2025-11-29"

    # 这里是几条 sample incidents，可以按喜好改 / 多加几条
    incidents = [
        {
            "created_at": f"{date_str}T01:20:00Z",
            "event_type": "EC2_HIGH_CPU",
            "instance_id": "i-samplecpu-001",
            "remediation_type": "EC2_HIGH_CPU",
            "action": "NO_ACTION",
            "message": "CPU reached 92% for over 3 minutes.",
            "success": True,
        },
        {
            "created_at": f"{date_str}T02:50:00Z",
            "event_type": "EC2_HIGH_CPU",
            "instance_id": "i-samplecpu-002",
            "remediation_type": "EC2_HIGH_CPU",
            "action": "REBOOT",
            "message": "High CPU persisted. Reboot attempted.",
            "success": True,
        },
        {
            "created_at": f"{date_str}T05:10:00Z",
            "event_type": "StatusCheckFailed",
            "instance_id": "i-samplestatus-001",
            "remediation_type": "EC2_STATUS_CHECK_FAILED",
            "action": "FAILED",
            "message": "StatusCheckFailed detected. Reboot dry-run failed.",
            "success": False,
        },
        {
            "created_at": f"{date_str}T09:00:00Z",
            "event_type": "UnexpectedStop",
            "instance_id": "i-samplestop-003",
            "remediation_type": "EC2_UNEXPECTED_STOP",
            "action": "STARTED",
            "message": "Instance unexpectedly stopped. Auto-start executed.",
            "success": True,
        },
    ]

    md = build_markdown_report(date_str, incidents)

    filename = f"{date_str}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Generated markdown report: {filename}")
