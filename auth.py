from passlib.context import CryptContext
import jwt
from dotenv import dotenv_values
from .models import User
fro
config credentials = dotenv_values("env")

pass_context = CryptContext(schemes = ['bcrypt'],deprecated='auto')

def get_hashed_password(password):
    return pass_context.hash(password)

async def very_token(token:str):
    try:
        """consists of user id"""
        payload = jwt.decode(token,config_credential['SECRET'])
        user = await User.get(id =payload.get("id"))# decode theuser  token
    except:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate":"NOT FOUND"}
                )
        return user
