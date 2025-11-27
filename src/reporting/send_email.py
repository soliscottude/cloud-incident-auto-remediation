import os
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

from ..utils.config import SES_SENDER, SES_RECIPIENT
from ..utils.logging_utils import get_logger, log_json

logger = get_logger(__name__)


def _get_recipients() -> List[str]:
    """
    Resolve SES recipients from configuration / environment.

    Priority:
    1) SES_RECIPIENTS env var (comma-separated list).
    2) SES_RECIPIENT from config (single recipient).
    """
    raw_recipients = os.getenv("SES_RECIPIENTS")
    if raw_recipients:
        recipients = [r.strip() for r in raw_recipients.split(",") if r.strip()]
        if recipients:
            return recipients

    if SES_RECIPIENT:
        return [SES_RECIPIENT]

    raise ValueError(
        "No SES recipients configured. "
        "Set SES_RECIPIENTS (comma-separated) or SES_RECIPIENT."
    )


def send_report_email(date_str: str, markdown_report: str) -> Dict[str, Any]:
    """
    Send the daily incident report via Amazon SES.

    The sender and recipients are resolved from configuration:
    - SES_SENDER: verified SES identity
    - SES_RECIPIENTS / SES_RECIPIENT: target inbox(es)
    """
    if not SES_SENDER:
        raise ValueError("SES_SENDER is not configured")

    recipients = _get_recipients()

    subject = f"Daily Incident Report - {date_str}"

    ses = boto3.client("ses")

    try:
        response = ses.send_email(
            Source=SES_SENDER,
            Destination={"ToAddresses": recipients},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": markdown_report, "Charset": "UTF-8"},
                },
            },
        )

        log_json(
            logger,
            "info",
            "Daily report email sent via SES",
            {
                "date": date_str,
                "sender": SES_SENDER,
                "recipients": recipients,
                "message_id": response.get("MessageId"),
            },
        )

        return {
            "status": "SUCCESS",
            "message_id": response.get("MessageId"),
            "recipients": recipients,
        }

    except ClientError as e:
        error_msg = str(e)
        log_json(
            logger,
            "error",
            "Failed to send daily report email via SES",
            {
                "date": date_str,
                "sender": SES_SENDER,
                "recipients": recipients,
                "error": error_msg,
            },
        )
        return {
            "status": "FAILED",
            "error": error_msg,
            "recipients": recipients,
        }
