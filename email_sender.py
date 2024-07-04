from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dontenv_values
from pydantic import BaseModel,EmailStr
config_credentials = dotenv_values(".env")
from typing import List
from .models import User
import jwt
conf = ConnectionConfig(
    MAIL_USERNAME=config_credentials["EMAIL"],
    MAIL_PASSWORD=config_credentials["PASSWORD"],
    MAIL_FROM=config_credentials["EMAIL"],
    MAIL_PORT=587,
    MAIL_SERVER="smpt.gmail.com",
    MAIL_SSL =False,
    MAIL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

html = """
<h1> Account Verification</h1>
<p>Thanks for using KeeperAPI</p>
<a href = "http://localhost:8000/verification/?token={token}> Verify your email</a>


"""

class EmailSchema(Basemodel):
    email : List{EmailStr]

async def Email_sender(email:EmailSchema,instance:User)
token_data = {
        "id" : instance.id,
        "username": instance.username
        }
token = jwt.encode(token_data,config_credentials["SECRET"])
   message = MessageSchema(
        subject= "KeeperAPI Account Verification Email",
        recipients=email#List emails,
        body=html,
        subtype=html
        )
   fm =FastMail(conf)
   awaitfm.send_message(message=message)
