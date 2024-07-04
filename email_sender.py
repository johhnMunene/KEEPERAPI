from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dontenv_values
from typing import LIst
import jwt
from .model import User




config_credentials = dotenv_values(".env")

conf = ConnectionConfig(
    MAIL_USERNAME=config_credentials["email"],
    MAIL_PASSWORD=""59b1a0f451e16d,
    MAIL_FROM="",
    MAIL_PORT=587,
    MAIL_SERVER="smpt.gmail.com",
    MAIL_SSL =False,
    MAIL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

html = """
<p>Thanks for using KeeperAPI</p>
<h> Account Verification</h1>
<br>
<p> click the button below to verify your account</p>
<a href="http"//localhost:/8000/verifcation/?token={token}">/a>
"""
class EmailSchema(Basemodel):
    email:List[EmailStr]
async def send_email(email:EmailSchema,instance:User):
    token_data = {
            "id " = instance.id,
            "username": instance.username
            }
    token = jwt.encode(token_data,config_credentials["SECRET"])
message = MessageSchema(
        subject = "Keeper Account Verification Email",
        recipients = email,
        body = html,
        subtype = "html"
        )
fm = FastMail(conf)
await fm.send_message(message=message)
