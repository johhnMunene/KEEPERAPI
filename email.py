from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel
from typing import List

class EmailSchema(BaseModel):
    email: List[str]

conf = ConnectionConfig(
    MAIL_USERNAME="your_username",
    MAIL_PASSWORD="your_password",
    MAIL_FROM="your_email@example.com",
    MAIL_PORT=465,
    MAIL_SERVER="your_mail_server",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

html = """
<p>Thanks for using KeeperAPI</p>
"""

async def send_email(email: str):
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=[email],  # List of emails
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

