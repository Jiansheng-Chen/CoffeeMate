from .database import CoffeeDB
from typing import AsyncGenerator, Optional
import logging      
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from jose import jwt, JWTError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from passlib.context import CryptContext
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "5b3c1cc0c03b8683ee2a027496031e160f6e911d958b3cbbac59b44ad2d3614f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


coffeedb = CoffeeDB()

async def get_db():
    if(coffeedb.db is not None):
        return coffeedb.db
    else:
        raise RuntimeError("数据库连接未建立！请检查应用启动日志。")



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    email:  Optional[str]  = None
    name:  Optional[str]  = None
    disabled:  Optional[bool]  = None
    permission:  Optional[list[str]] =None


class UserInDB(User):
    password_hashed: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(email: str, db: Annotated[Any, Depends(get_db)]):
    #print(f"input email: {email}")
    user_doc = await db.user.find_one({"email": email})
    if user_doc is None:
        return None
    user_doc.pop("_id", None)
    return UserInDB(**user_doc)


async def authenticate_user(email: str, password: str, db=Depends(get_db)):
    user = await get_user(email, db)
    #print(user)
    if not user:
        return False
    if not await verify_password(password, user.password_hashed):
        return False
    return user


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(token : str) -> dict:
    #验证token并且返回payload
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expire = payload.get("exp")
        if expire is None:
            raise JWTError("Token has no expiration time")
        if datetime.utcnow() >= datetime.fromtimestamp(expire):
            raise JWTError("Token has expired")
        return payload

    except JWTError as e:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = str(e) if str(e) in ["Token has no expiration time", "Token has expired"] else "Could not validate credentials",
            headers = {"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await verify_token(token)
        email = payload.get("sub")
        permission = payload.get("permission")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, permission=permission)
    except JWTError:
        raise credentials_exception
    user = await get_user(email=token_data.email, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_dialogue_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    if("dialogue" not in current_user.permission):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "user has no permission",
            headers={"WWW-Authenticate": "Bearer"}
        )
    else:
        return current_user

