# main.py

from fastapi import FastAPI, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from models import User, Keeper, Product
from auth import get_hashed_password

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
        # business_obj = await Business.create(
        #     business_name=instance.username,
        #     owner=instance
        # )
        # await business_pydantic.from_tortoise_orm(business_obj)
        # Send email here
        pass

# Pydantic models for serialization and validation
User_Pydantic = pydantic_model_creator(User, name="User", exclude=("is_verified",))
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))
Keeper_Pydantic = pydantic_model_creator(Keeper, name="Keeper")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/registrations")
async def register_user(user: UserIn_Pydantic):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = get_hashed_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await User_Pydantic.from_tortoise_orm(user_obj)
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

