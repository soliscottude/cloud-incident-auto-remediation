import os
import datetime
import json
from typing import Any, Dict

from .utils.aws_clients import get_s3_client
from .reporting.daily_report import build_daily_report
from .reporting.send_email import send_report_email


def upload_report_to_s3(date_str: str, markdown_report: str) -> Dict[str, Any]:
    """
    上传日报 Markdown 到 S3。
    """
    bucket = os.getenv("REPORT_BUCKET_NAME")
    if not bucket:
        raise ValueError("REPORT_BUCKET_NAME env var is not set")

    prefix = os.getenv("REPORT_PREFIX", "daily-reports/")
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    key = f"{prefix}{date_str}.md"

    s3 = get_s3_client()

    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=markdown_report.encode("utf-8"),
            ContentType="text/markdown; charset=utf-8",
        )
        return {"status": "SUCCESS", "bucket": bucket, "key": key}
    except Exception as e:
        return {"status": "FAILED", "error": str(e), "bucket": bucket, "key": key}


def _get_report_date_from_event(event: Dict[str, Any]) -> str:
    """从事件解析日期，不填则默认今天 UTC."""
    if isinstance(event, dict):
        if isinstance(event.get("date"), str):
            return event["date"]
        detail = event.get("detail") or {}
        if isinstance(detail.get("date"), str):
            return detail["date"]

    return datetime.datetime.utcnow().strftime("%Y-%m-%d")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """日报 Lambda 主入口。"""
    date_str = _get_report_date_from_event(event)

    markdown_report = build_daily_report(date_str)
    email_result = send_report_email(date_str, markdown_report)
    s3_result = upload_report_to_s3(date_str, markdown_report)

    return {
        "date": date_str,
        "email_result": email_result,
        "s3_result": s3_result,
    }


if __name__ == "__main__":
    """
    本地测试入口：
    直接用 python3 -m src.daily_report_lambda 来跑这段代码。
    """
    test_event = {"date": "2025-11-24"}  # 用你刚才有数据的那一天
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2, ensure_ascii=False))
