import os

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SES_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

ses_client = boto3.client("ses", region_name=AWS_REGION)


def _send_email(to_email: str, subject: str, text_body: str, html_body: str) -> None:
    ses_client.send_email(
        Source=SES_SENDER_EMAIL,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {
                "Text": {"Data": text_body},
                "Html": {"Data": html_body},
            },
        },
    )


def send_verification_email(to_email: str, token: str) -> None:
    link = f"{BACKEND_BASE_URL}/api/auth/verify-email?token={token}"
    subject = "Verify your AutoAssist email"
    text_body = (
        "Welcome to AutoAssist.\n\n"
        f"Verify your email by visiting this link:\n{link}\n\n"
        "This link expires in 24 hours."
    )
    html_body = f"""
    <html>
      <body style="font-family: sans-serif;">
        <h2>Welcome to AutoAssist</h2>
        <p>Click the link below to verify your email address:</p>
        <p><a href="{link}">Verify Email</a></p>
        <p style="color: #666; font-size: 14px;">This link expires in 24 hours.</p>
      </body>
    </html>
    """
    _send_email(to_email, subject, text_body, html_body)


def send_password_reset_email(to_email: str, token: str) -> None:
    link = f"{FRONTEND_BASE_URL}/?reset_token={token}"
    subject = "Reset your AutoAssist password"
    text_body = (
        "A password reset was requested for your AutoAssist account.\n\n"
        f"Reset your password by visiting this link:\n{link}\n\n"
        "This link expires in 1 hour. If you didn't request this, you can ignore this email."
    )
    html_body = f"""
    <html>
      <body style="font-family: sans-serif;">
        <h2>Reset your password</h2>
        <p>Click the link below to reset your AutoAssist password:</p>
        <p><a href="{link}">Reset Password</a></p>
        <p style="color: #666; font-size: 14px;">
          This link expires in 1 hour. If you didn't request this, you can ignore this email.
        </p>
      </body>
    </html>
    """
    _send_email(to_email, subject, text_body, html_body)
