import logging
from passlib.context import CryptContext
import jwt
from dotenv import dotenv_values
from fastapi import HTTPException, status
from models import User

from fastapi import FastAPI, Request
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

config_credentials = dotenv_values(".env")

pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    return pass_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.debug("Verifying password")
    return pass_context.verify(plain_password, hashed_password)

async def authenticate_user(username: str, password: str):
    logger.debug(f"Authenticating user: {username}")
    user = await User.get(username=username)
    if user and await verify_password(password, user.password):
        logger.debug(f"User {username} authenticated successfully")
        return user
    logger.debug(f"User {username} authentication failed")
    return None

async def token_generator(username: str, password: str):
    logger.debug(f"Generating token for user: {username}")
    user = await authenticate_user(username, password)
    if not user:
        logger.debug(f"Token generation failed for user: {username}")
        return None
    token_data = {
        "id": user.id,
        "username": user.username
    }
    token = jwt.encode(token_data, config_credentials['SECRET'], algorithm='HS256')
    logger.debug(f"Token generated for user: {username}")
    return token

async def verify_token(token: str):
    logger.debug("Verifying token")
    try:
        payload = jwt.decode(token, config_credentials['SECRET'], algorithms=["HS256"])
        user = await User.get(id=payload.get("id"))
        logger.debug(f"Token verified for user ID: {payload.get('id')}")
        return user
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

