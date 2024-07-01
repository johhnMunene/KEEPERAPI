from fastapi import FastAPI, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from models import User, Keeper, Product
from auth import get_hashed_password

# Pydantic models for serialization and validation
User_Pydantic = pydantic_model_creator(User, name="User", exclude=("is_verified",))
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))
Keeper_Pydantic = pydantic_model_creator(Keeper, name="Keeper")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/registrations")
async def register_user(user: UserIn_Pydantic):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = get_hashed_password(user_info["password"])  # Assuming get_hashed_password is correctly implemented
    user_obj = await User.create(**user_info)
    return await UserOut_Pydantic.from_tortoise_orm(user_obj)

register_tortoise(
    app,
    db_url='mysql://username:password@localhost:3306/mydatabase',
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

