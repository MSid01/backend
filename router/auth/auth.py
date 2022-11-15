from datetime import timedelta

from database import schemas
from database.dependency import get_db
from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException,
                     Response, status)
from fastapi.security import OAuth2PasswordRequestForm
from router.auth.auth_functions import (authenticate_user, create_access_token,
                                        sign_up_user, verify_user)
from router.auth.config import Settings, get_settings
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/signup/", response_model=schemas.MessageWithStatus)
async def signup(user: schemas.UserCreate,background_tasks: BackgroundTasks,db: Session = Depends(get_db)):
    return await sign_up_user(db,user,background_tasks)
            
@router.get("/verification/{token}/")#, status_code=201, response_model=schemas.MessageWithStatus)
def verification(token: str, db: Session = Depends(get_db)):
    return verify_user(db,token)

@router.post("/token/", response_model=schemas.Token)
async def login_for_access_token(response: Response,form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db),settings:Settings=Depends(get_settings)):
    user = authenticate_user(db, form_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True,samesite="strict")  #set HttpOnly cookie in response
    return {"access_token": access_token, "token_type": "bearer"}
