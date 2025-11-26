# src/reporting/send_email.py

import os
from typing import List, Dict, Any

from ..utils.aws_clients import get_ses_client
from botocore.exceptions import ClientError


def _parse_recipients(value: str) -> List[str]:
    """将逗号分隔的邮箱字符串转成列表。"""
    return [addr.strip() for addr in value.split(",") if addr.strip()]


def send_report_email(date_str: str, markdown_report: str) -> Dict[str, Any]:
    """
    发送日报邮件。

    需要环境变量：
    - SES_SENDER
    - SES_RECIPIENTS
    """
    sender = os.getenv("SES_SENDER")
    recipients_raw = os.getenv("SES_RECIPIENTS", "")

    if not sender:
        raise ValueError("SES_SENDER env var is not set")

    recipients = _parse_recipients(recipients_raw)
    if not recipients:
        raise ValueError("SES_RECIPIENTS env var is not set or empty")

    subject = f"Daily Cloud Incident Report - {date_str}"
    body_text = markdown_report

    ses = get_ses_client()  # ← 统一用你的 aws_clients

    try:
        response = ses.send_email(
            Source=sender,
            Destination={"ToAddresses": recipients},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body_text, "Charset": "UTF-8"}},
            },
        )

        return {
            "status": "SUCCESS",
            "message_id": response["MessageId"],
            "recipients": recipients,
        }

    except ClientError as e:
        return {
            "status": "FAILED",
            "error": str(e),
            "recipients": recipients,
        }
