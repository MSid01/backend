from typing import List

from database.dependency import get_db
from database.schemas import (UpdatedProfileSchema, UserBase,
                              UserComplaintsResponse, UserProfileBaseSchema,
                              UserProfileSchema)
from fastapi import APIRouter, Depends, HTTPException, status
from router.auth.auth_functions import get_current_active_user
from router.users.user_functions import (get_user_complaints, get_user_profile,
                                         reform_user_profile)
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

@router.get("/profile/", response_model=UserProfileSchema)
def read_user_profile(current_user: UserBase = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return get_user_profile(current_user, db)

@router.patch("/profile/", response_model=UpdatedProfileSchema)
def update_user_profile(user_profile:UserProfileBaseSchema,current_user: UserProfileSchema = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return reform_user_profile(user_profile,current_user, db)


@router.get("/complaints/", response_model=List[UserComplaintsResponse])
def read_user_complaints( db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    return get_user_complaints(username=current_user.username, db=db)

