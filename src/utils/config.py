import os

# DynamoDB Table
INCIDENT_TABLE_NAME = os.getenv("INCIDENT_TABLE_NAME", "incident_events")

# S3 bucket
REPORT_BUCKET_NAME = os.getenv("REPORT_BUCKET_NAME", "")
REPORT_PREFIX = os.getenv("REPORT_PREFIX", "daily-reports/")

# SES
SES_SENDER = os.getenv("SES_SENDER", "")
SES_RECIPIENT = os.getenv("SES_RECIPIENT", "")


def validate_basic_config() -> None:
    """
    可选：在 Lambda 初始化时检查关键配置是否为空。
    你可以在 handler 顶部调用一下这个函数，发现配置不对就打日志。
    """
    missing = []
    if not INCIDENT_TABLE_NAME:
        missing.append("INCIDENT_TABLE_NAME")
    if not REPORT_BUCKET_NAME:
        missing.append("REPORT_BUCKET_NAME")
    if not SES_SENDER:
        missing.append("SES_SENDER")
    if not SES_RECIPIENT:
        missing.append("SES_RECIPIENT")

    if missing:

        print(f"[config] Missing important environment variables: {', '.join(missing)}")
