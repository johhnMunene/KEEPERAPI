from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import jwt
from pydantic import EmailStr
from models import User  # Adjust the import as per your project structure
import os
from typing import List

load_dotenv()  # Load environment variables from .env file

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("EMAIL"),
    MAIL_PASSWORD=os.getenv("PASS"),
    MAIL_FROM=os.getenv("EMAIL"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",  # Correct SMTP server for Gmail
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)
async def send_mail(email: List[EmailStr], instance: User):
    """Send Account Verification email"""

    token_data = {
        "id": instance.id,
        "username": instance.username,
        "email": instance.email
    }

    token = jwt.encode(token_data, config_credentials["SECRET"], algorithm="HS256")

    template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <div style="display: flex; align-items: center; flex-direction: column;">
            <h3>Account Verification</h3>
            <br>
            <p>
                Thank you for choosing {SITE_NAME}. Please click on the button below
                to verify your account:
            </p>
            <a style="display: block; margin-top: 1rem; padding: 1rem; border-radius: 0.5rem;
                      font-size: 1rem; text-decoration: none; background: #0275d8; color: white;"
               href="{SITE_URL}/verification/email/?token={token}">
                Verify your email
            </a>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=f"{SITE_NAME} Account Verification",
        recipients=email,
        body=template,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

