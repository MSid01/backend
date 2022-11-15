
import io
from datetime import datetime, timedelta
from typing import Union

import pyotp
import qrcode
import qrcode.image.svg
from fastapi import Depends, HTTPException, status
# from api.utils import OAuth2PasswordBearerWithCookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from database import models, schemas
from database.crud import (get_ward_servant_by_email,
                           get_ward_servant_by_username, get_ward_servant_info)
from database.dependency import get_db
from router.auth.config import Settings, get_settings

auth_config_settings:Settings = get_settings()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authority/auth/token")

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
    user = get_ward_servant_by_username(db, form_data.username)
    if not user:
        return False
    if not verify_password(form_data.password[:-6], user.hashed_password):
        return False
    totp = pyotp.TOTP(user.secret_key)
    if not totp.verify(form_data.password[-6:]):
        return False
    return user

#create user function
async def create_user(db: Session, user: schemas.WardServantCreate):
    user_info = get_ward_servant_info(db,user.email)
    if not user_info:
        raise HTTPException(status_code=400, detail="You are not allowed to Sign up")
    if user_info.password != user.temp_password:
        raise HTTPException(status_code=400, detail="temp_password is not correct")
    user.password = get_password_hash(user.password)
    db_user = models.WardServant(
        id = user_info.id,
        username = user_info.username,
        email = user_info.email,
        hashed_password = user.password,
        secret_key = user_info.secret_key)

    db_user_profile = models.WardServantProfile(
        username = user_info.username,
        first_name = user_info.first_name,
        last_name = user_info.last_name,
        phone_number = user_info.phone_number,
        ward_id = user_info.ward_id,
        position = user_info.position
    )
    db.add(db_user)
    db.add(db_user_profile)
    db.commit()
    db.refresh(db_user)
    db.refresh(db_user_profile)
    provisioning_URI = pyotp.totp.TOTP(db_user.secret_key).provisioning_uri(name=db_user.username, issuer_name="Citizen")
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(provisioning_URI, image_factory=factory)
    buffer = io.BytesIO()
    img.save(buffer)
    db_user_profile.qr_code = buffer.getvalue().replace(b'\n', b'')
    db_user_profile.qr_code = db_user_profile.qr_code.replace(b'\\', b'')
    return db_user_profile


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
    user = get_ward_servant_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def sign_up_user(db: Session,user: schemas.WardServantCreate):
    if not user.email:
        raise HTTPException(status_code=400, detail="email is required")
    if not user.password:
        raise HTTPException(status_code=400, detail="password is required")
    if not user.temp_password:
        raise HTTPException(status_code=400, detail="temp_password is required")
    db_email = get_ward_servant_by_email(db,user.email)
    if db_email:
        raise HTTPException(status_code=400, detail="email already exists")
    return await create_user(db=db,user=user)


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
