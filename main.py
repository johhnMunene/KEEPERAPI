from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from models import User, Keeper, Product
from auth import get_hashed_password, token_generator, verify_token
from fastapi.logger import logger
from tortoise.exceptions import IntegrityError
from pydantic import BaseModel
from email_sender import send_email
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()
templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# Pydantic models
User_Pydantic = pydantic_model_creator(User, name="User", exclude=("is_verified",))
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))
Keeper_Pydantic = pydantic_model_creator(Keeper, name="Keeper")

# Token generation endpoint
@app.post("/token")
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return {"access_token": token, "token_type": "bearer"}

# Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await verify_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

@app.get("/user/me")
async def user_login(user: User_Pydantic = Depends(get_current_user)):
    business = await Keeper.get(owner=user)
    return {
        "status": "ok",
        "data": {
            "username": user.username,
            "email": user.email,
            "verified": user.is_verified,
            "joined_date": user.join_date.strftime("%d %d %Y")
        }
    }

# Post-save signal to send email
@post_save(User)
async def create_business(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str]
) -> None:
    if created:
        await send_email([instance.email], instance)

class RegistrationResponse(BaseModel):
    status: str
    data: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/registrations", response_model=RegistrationResponse)
async def register_user(user: UserIn_Pydantic, request: Request):
    user_info = user.dict(exclude_unset=True)
    logger.info(f"Incoming registration data: {user_info}")

    existing_user = await User.filter(email=user_info["email"]).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    existing_user = await User.filter(username=user_info["username"]).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken."
        )

    user_info["password"] = get_hashed_password(user_info["password"])

    try:
        user_obj = await User.create(**user_info)
        new_user = await User_Pydantic.from_tortoise_orm(user_obj)

        # Send confirmation email
        await send_email([new_user.email], new_user)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user. Email or username may already exist."
        )

    return {
        "status": "ok",
        "data": f"Hello {new_user.username}, thanks for using KEEPERAPI. Check your email to confirm your registration."
    }

@app.get('/verification', response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await verify_token(token)  # Ensure verify_token is correctly implemented

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse("verification.html", {"request": request, "username": user.username})

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "NOT FOUND"}
    )

# Register Tortoise ORM
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",  # Use your actual database URL
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)

# Start the application
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

