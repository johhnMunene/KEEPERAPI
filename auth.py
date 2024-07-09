from passlib.context import CryptContext
import jwt
from dotenv import dotenv_values
from fastapi import HTTPException, status
from models import User

config_credentials = dotenv_values(".env")

pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_hashed_password(password: str) -> str:
    return pass_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pass_context.verify(plain_password, hashed_password)

async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)
    if user and await verify_password(password, user.password):
        return user
    return None

async def token_generator(username: str, password: str):
    user = await authenticate_user(username, password)
    if not user:
        return None
    token_data = {
        "id": user.id,
        "username": user.username
    }
    token = jwt.encode(token_data, config_credentials['SECRET'], algorithm='HS256')
    return token

async def verify_token(token: str):
    try:
        payload = jwt.decode(token, config_credentials['SECRET'], algorithms=["HS256"])
        user = await User.get(id=payload.get("id"))
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

