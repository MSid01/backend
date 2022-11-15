from datetime import datetime, timedelta
from typing import Union

from fastapi import BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
# from api.utils import OAuth2PasswordBearerWithCookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from requests import request
from sqlalchemy.orm import Session

from database import models, schemas
from database.crud import (get_user_by_email, get_user_by_temp_email,
                           get_user_by_temp_username, get_user_by_username)
from database.dependency import get_db
from database.email_verification import send_verification_email
from router.auth.config import Settings, get_settings

auth_config_settings:Settings = get_settings()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# get password hash
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str, ):
    return pwd_context.verify(plain_password, hashed_password)

# create access token
def create_access_token(data: dict, expires_delta: Union[timedelta , None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, auth_config_settings.SECRET_KEY, algorithm=auth_config_settings.ALGORITHM)
    return encoded_jwt

def authenticate_user(db:Session, form_data: schemas.UserLogin):
    user = get_user_by_username(db, form_data.username)
    if not user:
        return False
    if not verify_password(form_data.password, user.hashed_password):
        return False
    return user

#create user function
async def create_user(db: Session, user: schemas.UserCreate, background_tasks: BackgroundTasks):
    user.password = get_password_hash(user.password)
    db_user = models.TemporaryUser(
        username=user.username,
        email=user.email,
        hashed_password=user.password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    temp_access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=auth_config_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return await send_verification_email(user.email, temp_access_token, background_tasks)

# verify user
def verify_user(db: Session, token: str):
    try:
        payload = jwt.decode(token, auth_config_settings.SECRET_KEY, algorithms=[auth_config_settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise JWTError()
            # return RedirectResponse(f'{FRONT_END_URL}/auth/login', status_code=status.HTTP_401_UNAUTHORIZED)
        temp_user = get_user_by_temp_username(db,username)
        if temp_user is None:
            raise JWTError()
            # return RedirectResponse(f'{FRONT_END_URL}/auth/login', status_code=status.HTTP_401_UNAUTHORIZED)
        user_model = models.User(
            username= temp_user.username,
            email= temp_user.email,
            hashed_password= temp_user.hashed_password,
            is_active= temp_user.is_active,
            created_at= temp_user.created_at)
        db.add(user_model)
        db.delete(temp_user)
        db.commit()
        db.refresh(user_model)

        user_profile = models.UserProfile(
            username= user_model.username,
        )
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)
        return RedirectResponse('{}/auth/login'.format(auth_config_settings.FRONT_END_URL))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
async def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth_config_settings.SECRET_KEY, algorithms=[auth_config_settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def check_disposable_email(email: EmailStr):
    url = "https://mailcheck.p.rapidapi.com/"

    querystring = {"domain":email}

    headers = {
	"X-RapidAPI-Key": auth_config_settings.RAPIDAPI_KEY,
	"X-RapidAPI-Host": auth_config_settings.RAPIDAPI_HOST
}

    response = request("GET", url, headers=headers, params=querystring).json()
    return response["disposable"]

async def sign_up_user(db: Session,user: schemas.UserCreate,background_tasks: BackgroundTasks):
    is_disposable_email = await check_disposable_email(user.email)
    if is_disposable_email:
        raise HTTPException(status_code=400, detail="Disposable email not allowed")
    if not user.username:
        raise HTTPException(status_code=400, detail="username is required")
    if not user.email:
        raise HTTPException(status_code=400, detail="email is required")
    if not user.password:
        raise HTTPException(status_code=400, detail="password is required")
    db_username = get_user_by_username(db,user.username)
    if db_username:
        raise HTTPException(status_code=400, detail="username already exists")
    db_temp_username = get_user_by_temp_username(db,user.username)
    if db_temp_username:
        raise HTTPException(status_code=400, detail="username already exists")
    db_temp_email = get_user_by_temp_email(db,user.email)
    if db_temp_email:
        raise HTTPException(status_code=400, detail="email already exists")
    db_user_email = get_user_by_email(db,email=user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await create_user(db=db,user=user,background_tasks=background_tasks)


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
