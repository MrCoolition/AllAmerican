from __future__ import annotations

from typing import Any, Dict

import boto3
from botocore.client import BaseClient

from .config import settings


def _get_ses_client() -> BaseClient:
    session_kwargs: Dict[str, Any] = {}
    client_kwargs: Dict[str, Any] = {}

    if settings.AWS_SES_ACCESS_KEY_ID and settings.AWS_SES_SECRET_ACCESS_KEY:
        session_kwargs["aws_access_key_id"] = settings.AWS_SES_ACCESS_KEY_ID
        session_kwargs["aws_secret_access_key"] = settings.AWS_SES_SECRET_ACCESS_KEY

    session = boto3.session.Session(**session_kwargs) if session_kwargs else boto3.session.Session()

    if settings.AWS_SES_REGION:
        client_kwargs["region_name"] = settings.AWS_SES_REGION

    return session.client("ses", **client_kwargs)


def send_email(to_email: str, subject: str, html: str) -> None:
    client = _get_ses_client()

    message: Dict[str, Any] = {
        "Source": settings.FROM_EMAIL,
        "Destination": {"ToAddresses": [to_email]},
        "Message": {
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {"Html": {"Data": html, "Charset": "UTF-8"}},
        },
    }

    if settings.AWS_SES_CONFIGURATION_SET:
        message["ConfigurationSetName"] = settings.AWS_SES_CONFIGURATION_SET

    client.send_email(**message)
