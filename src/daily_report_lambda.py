import json
import datetime
from typing import Any, Dict

from .utils.aws_clients import get_s3_client
from .utils.config import REPORT_BUCKET_NAME, REPORT_PREFIX
from .utils.logging_utils import get_logger, log_json
from .reporting.daily_report import build_daily_report
from .reporting.send_email import send_report_email

logger = get_logger(__name__)


def upload_report_to_s3(date_str: str, markdown_report: str) -> Dict[str, Any]:
    """
    Upload the daily incident report (Markdown) to S3.

    The target bucket and prefix are controlled via configuration
    (REPORT_BUCKET_NAME, REPORT_PREFIX), typically set by environment variables.
    """
    bucket = REPORT_BUCKET_NAME
    if not bucket:
        # Fail fast if configuration is missing.
        raise ValueError("REPORT_BUCKET_NAME is not configured")

    prefix = REPORT_PREFIX or "daily-reports/"
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
            ContentDisposition="inline",
        )
        log_json(
            logger,
            "info",
            "Daily report uploaded to S3",
            {"bucket": bucket, "key": key, "date": date_str},
        )
        return {"status": "SUCCESS", "bucket": bucket, "key": key}
    except Exception as e:
        error_msg = str(e)
        log_json(
            logger,
            "error",
            "Failed to upload daily report to S3",
            {"bucket": bucket, "key": key, "date": date_str, "error": error_msg},
        )
        return {"status": "FAILED", "error": error_msg, "bucket": bucket, "key": key}


def _get_report_date_from_event(event: Dict[str, Any]) -> str:
    """
    Derive the report date from the incoming event.

    Priority:
    1) event["date"]
    2) event["detail"]["date"]
    3) Fallback to today's date in UTC (YYYY-MM-DD)
    """
    if isinstance(event, dict):
        if isinstance(event.get("date"), str):
            return event["date"]

        detail = event.get("detail") or {}
        if isinstance(detail.get("date"), str):
            return detail["date"]

    return datetime.datetime.utcnow().strftime("%Y-%m-%d")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main entry point for the Daily Report Lambda.

    Steps:
    1. Determine which date to build the report for.
    2. Generate the Markdown daily report from DynamoDB.
    3. Send the report via SES.
    4. Upload the report to S3 for archival.
    """
    date_str = _get_report_date_from_event(event)
    log_json(
        logger,
        "info",
        "Daily report Lambda triggered",
        {"date": date_str, "raw_event": event},
    )

    # Build Markdown report content from DynamoDB incidents.
    markdown_report = build_daily_report(date_str)

    # Send the report via SES.
    email_result = send_report_email(date_str, markdown_report)

    # Upload the report to S3.
    s3_result = upload_report_to_s3(date_str, markdown_report)

    result = {
        "date": date_str,
        "email_result": email_result,
        "s3_result": s3_result,
    }

    log_json(
        logger,
        "info",
        "Daily report Lambda execution completed",
        result,
    )

    return result


if __name__ == "__main__":
    """
    Local test entrypoint.
    Run with:
        python3 -m src.daily_report_lambda
    """
    import os

    # ⚠ Local-only defaults for testing.
    # In real Lambda, these should be set via environment variables.
    os.environ.setdefault("SES_SENDER", "scogranger@gmail.com")
    os.environ.setdefault("SES_RECIPIENT", "scogranger@gmail.com")
    os.environ.setdefault("REPORT_BUCKET_NAME", "cloud-incident-reports-scott")
    os.environ.setdefault("REPORT_PREFIX", "daily-reports/")
    os.environ.setdefault("INCIDENT_TABLE_NAME", "incident_events")

    test_event: Dict[str, Any] = {"date": "2025-11-24"}
    output = lambda_handler(test_event, context=None)
    print(json.dumps(output, indent=2, ensure_ascii=False))
