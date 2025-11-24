import os
from typing import Any
from boto3.session import Session

DEFAULT_REGION = "ap-southeast-2"
AWS_REGION = os.getenv("AWS_REGION", DEFAULT_REGION)
AWS_PROFILE = os.getenv("AWS_PROFILE", None)

if AWS_PROFILE:
    session = Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
else:
    session = Session(region_name=AWS_REGION)


def get_ec2_client() -> Any:
    return session.client("ec2")


def get_dynamodb_client() -> Any:
    return session.client("dynamodb")


def get_ses_client() -> Any:
    return session.client("ses")
