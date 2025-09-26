from fastapi import APIRouter, Depends, HTTPException, status, Form
from typing import Annotated
from fastapi.responses import JSONResponse
from ..dependencies import ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user,get_db, authenticate_user, create_access_token, User, Token, get_current_active_user, get_user, get_password_hash
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description" : "Not found"}},
)

@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db = Depends(get_db)
) -> Token:
    #OAuth2PasswordRequestForm标准要求属性只有
    # username 
    # password
    # grant_type
    # scope
    # client_id
    # client_secret
    # 但这里其实传入的是email
    #print(f"login {form_data.username, form_data.password}")
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.email, "permission": user.permission}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.post("/register")
async def register(email: str = Form(), name : str = Form(), password : str = Form(), db=Depends(get_db)):
    user = await db.user.find_one({"email": email})
    if(user is None):
        password_hashed = await get_password_hash(password)
        await db.user.insert_one({"email":email, "name": name, "password_hashed": password_hashed, "disabled": False,"permission": ["dialogue"]})
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"success": True, "message": "User registered successfully"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )






