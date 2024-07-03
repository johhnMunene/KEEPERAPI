# main.py
from fastapi import FastAPI, HTTPException, Request, status
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from models import User, Keeper, Product
from auth import get_hashed_password
from fastapi.logger import logger
from tortoise.exceptions import IntegrityError
from pydantic import BaseModel

# Signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient

app = FastAPI()

@post_save(User)
async def create_business(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str]
) -> None:
    if created:
        pass

User_Pydantic = pydantic_model_creator(User, name="User", exclude=("is_verified",))
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))
Keeper_Pydantic = pydantic_model_creator(Keeper, name="Keeper")

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
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user. Email or username may already exist."
        )

    return {
        "status": "ok",
        "data": f"Hello {new_user.username}, thanks for using KEEPERAPI. Check your email to confirm your registration."
    }

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",  # Use your actual database URL
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

