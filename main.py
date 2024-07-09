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
from pydantic import BaseSettings
from pydantic_settings import BaseSettings



# Define Pydantic models
User_Pydantic = pydantic_model_creator(User, name="User", exclude=("is_verified",))
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))
Keeper_Pydantic = pydantic_model_creator(Keeper, name="Keeper")


# FastAPI application setup
app = FastAPI(
    title="KEEPER API",
    version="0.1.1",
    description="E-con API created with FastAPI and JWT authentication"
)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Token generation endpoint
@app.post("/token", tags=["User"])
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {"access_token": token, "token_type": "bearer"}

# Retrieve current user
async def get_current_user(token: str = Depends(oauth_scheme)):
    return await very_token(token)

# Endpoint to retrieve current user data
@app.post("/users/me", tags=["User"])
async def client_data(user: UserIn_Pydantic = Depends(get_current_user)):
    business = await Business.get(owner=user)
    logo = f'{SITE_URL}{business.logo}'
    return {
        "status": "ok",
        "data": {
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_verified,
            "join_date": user.join_date.strftime("%b %d %Y"),
            "logo": logo,
            "business": await business_pydantic.from_tortoise_orm(business)
        }
    }

# Endpoint to retrieve users
@app.get("/users/", tags=["User"], response_model=List[UserOut_Pydantic])
async def get_users(
    user: UserIn_Pydantic = Depends(get_current_user),
   ):
    users = await User.filter(id__gt=skip, id__lte=skip+limit)
    return users

# Signal handler to create business upon user creation
@post_save(User)
async def create_business(
    sender: Type[User],
    instance: User,
    created: bool,
    using_db: Optional[BaseDBAsyncClient],
    update_fields: List[str]
) -> None:
    if created:
        business_obj = await Business.create(
            business_name=instance.username,
            owner=instance
        )
        await business_pydantic.from_tortoise_orm(business_obj)
        await send_mail([instance.email], instance)

# Endpoint to update business details
@app.put("/business/{id}", response_model=business_pydantic, tags=["Business"])
async def update_business(
    id: int,
    update_business: business_pydanticIn,
    user: UserIn_Pydantic = Depends(get_current_user)
):
    business = await Business.get(id=id)
    owner = await business.owner
    update_business = update_business.dict()

    if user == owner:
        await business.update_from_dict(update_business)
        await business.save()
        return await business_pydantic.from_tortoise_orm(business)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated to perform this action",
        headers={"WWW-Authenticate": "Bearer"}
    )

# Endpoint to register a new user
@app.post("/users/", tags=["User"], status_code=status.HTTP_201_CREATED, response_model=user_pydanticOut)
async def user_registration(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)

    # This is a bad way to do it:
    # TODO fix this, create custom 'user_pydanticIn for validate data '
    if len(user_info["password"]) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be longer than 8 characters")
    if len(user_info["username"]) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username must be longer than 5 characters")
    if is_not_email(user_info["email"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This is not a valid email")

    if await User.exists(username=user_info.get("username")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    if await User.exists(email=user_info.get("email")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    user_info["password"] = get_hashed_password(user_info["password"])

    user_obj = await User.create(**user_info)
    user_new = await user_pydanticOut.from_tortoise_orm(user_obj)
    return user_new



# Endpoint for email verification
@app.get("/verification/email", response_class=HTMLResponse, tags=["User"])
async def email_verification(request: Request, token: str):
    user = await very_token_email(token)
    if user:
        if not user.is_verified:
            user.is_verified = True
            await user.save()
        context = {
            "request": request,
            "is_verified": user.is_verified,
            "username": user.username
        }
        return template.TemplateResponse("verification.html", context)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Token or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )



# Register Tortoise ORM with FastAPI
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)

