from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dotenv_values
from typing import List
import jwt
from pydantic import BaseModel, EmailStr
from models import User  # Adjust the import as per your project structure
from auth import *
config_credentials = dotenv_values(".env")

conf = ConnectionConfig(
    MAIL_USERNAME=config_credentials["EMAIL"],
    MAIL_PASSWORD=config_credentials["PASS"],  # Use the correct keys
    MAIL_FROM=config_credentials["EMAIL"],
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,  # Use MAIL_STARTTLS instead of MAIL_TLS
    MAIL_SSL_TLS=False,  # Use MAIL_SSL_TLS instead of MAIL_SSL
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

html = """
<p>Thanks for using KeeperAPI</p>
<h>Account Verification</h1>
<br>
<p>Click the button below to verify your account</p>
<a href="http://localhost:8000/verification/?token={token}">Verify Account</a>
"""

class EmailSchema(BaseModel):
    email: List[EmailStr]

async def send_email(email: EmailSchema, instance: User):
    token_data = {
        "id": instance.id,
        "username": instance.username
    }
    token = jwt.encode(token_data, config_credentials["SECRET"], algorithm="HS256")

    message = MessageSchema(
        subject="Keeper Account Verification Email",
        recipients=email.email,
        body=html.format(token=token),
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message=message)

