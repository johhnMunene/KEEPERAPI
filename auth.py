from passlib.context import CryptContext
import jwt
from dotenv import dotenv_values
from fastapi import HTTPException, status
from models import User

config_credentials = dotenv_values(".env")

pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_hashed_password(password: str) -> str:
    return pass_context.hash(password)

async def verify_token(token: str):
    try:
        """Decode the token to get the user id."""
        payload = jwt.decode(token, config_credentials['SECRET'], algorithms=["HS256"])
        user = await User.get(id=payload.get("id"))  # Decode the user token
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

