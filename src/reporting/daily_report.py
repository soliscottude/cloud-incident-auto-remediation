import os
import sys
import datetime
import collections
from typing import List, Dict, Optional

import boto3
from boto3.dynamodb.conditions import Attr


def get_dynamodb_table(table_name: str):

    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(table_name)


def get_incidents_for_date(table, date_str: str) -> List[Dict]:

    items: List[Dict] = []

    # 第一次 scan
    response = table.scan(FilterExpression=Attr("created_at").begins_with(date_str))
    items.extend(response.get("Items", []))

    # 如果有分页，继续 scan
    while "LastEvaluatedKey" in response:
        response = table.scan(
            FilterExpression=Attr("created_at").begins_with(date_str),
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        items.extend(response.get("Items", []))

    return items


def generate_markdown(date_str: str, incidents: List[Dict]) -> str:
    """根据你的表结构，生成 Markdown 报告。"""
    lines: List[str] = []

    lines.append(f"# Daily Cloud Incident Report - {date_str}")
    lines.append("")

    if not incidents:
        lines.append("No incidents recorded for this date.")
        return "\n".join(lines)

    # === Summary 区块 ===
    total = len(incidents)

    # 这里你没有 status 字段，我们可以根据 action / message 粗略判断
    # 比如：包含 "FAILED" 的算失败，这只是一个简单 heuristics
    failed_count = sum(
        1
        for i in incidents
        if "FAILED" in (i.get("action", "") + i.get("message", "")).upper()
    )
    success_count = total - failed_count

    # 统计唯一实例
    instance_ids = {i.get("instance_id") for i in incidents if i.get("instance_id")}
    unique_instances = len(instance_ids)

    # 按 event_type 统计数量
    by_event_type = collections.Counter(
        i.get("event_type", "UNKNOWN") for i in incidents
    )

    # 按 remediation_type 统计数量（你未来汇报的时候这块很好用）
    by_remediation_type = collections.Counter(
        i.get("remediation_type", "UNKNOWN") for i in incidents
    )

    lines.append("**Summary**")
    lines.append(f"- Total incidents: {total}")
    lines.append(f"- Success (heuristic): {success_count}")
    lines.append(f"- Failed (heuristic): {failed_count}")
    lines.append(f"- Unique instances: {unique_instances}")
    lines.append("")

    lines.append("**By event type**")
    for event_type, count in by_event_type.most_common():
        lines.append(f"- {event_type}: {count}")
    lines.append("")

    lines.append("**By remediation type**")
    for r_type, count in by_remediation_type.most_common():
        lines.append(f"- {r_type}: {count}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === 详情表格 ===
    lines.append("## Incident Details")
    lines.append("")
    lines.append(
        "| Time (created_at) | Event Type | Instance ID | Remediation Type | Action | Message |"
    )
    lines.append(
        "|-------------------|------------|-------------|------------------|--------|---------|"
    )

    def _sort_key(item: Dict):
        # 用 created_at 排序（如果有的话）
        return item.get("created_at", "")

    for item in sorted(incidents, key=_sort_key):
        created_at = item.get("created_at", "-")
        event_type = item.get("event_type", "-")
        instance_id = item.get("instance_id", "-")
        remediation_type = item.get("remediation_type", "-")
        action = item.get("action", "-")
        message = item.get("message", "").replace("\n", " ")

        if len(message) > 80:
            message = message[:77] + "..."

        lines.append(
            f"| {created_at} | {event_type} | {instance_id} | "
            f"{remediation_type} | {action} | {message} |"
        )

    return "\n".join(lines)


def build_daily_report(date_str: Optional[str] = None) -> str:

    table_name = os.getenv("INCIDENT_TABLE_NAME", "incident_events")
    table = get_dynamodb_table(table_name)

    if date_str is None:
        date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    incidents = get_incidents_for_date(table, date_str)
    markdown = generate_markdown(date_str, incidents)
    return markdown


def main():
    """Allow running the report locally: python daily_report.py 2025-11-26"""
    # 从命令行参数拿日期，不传则用今天
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    report = build_daily_report(date_str)
    print(report)


if __name__ == "__main__":
    main()
