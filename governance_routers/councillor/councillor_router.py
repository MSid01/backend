from database.db import SessionLocal
from database.dependency import get_db
from database.schemas import (CommentCreate, CommentResponse,
                              ComplaintUpdateBase, ComplaintUpdateResponse,
                              UserBase)
from fastapi import APIRouter, Depends, Query
from governance_routers.auth_router.auth_functions import get_current_user
from governance_routers.councillor.councillor_functions import \
    give_complaint_updates
from router.complaints.complaints_functions import create_comment

router = APIRouter(
    prefix="/councillor",
    tags=["councillor"],
    responses={404: {"description": "Not found"}},
)

@router.post("/make_updates", response_model= ComplaintUpdateResponse)
async def make_updates(complaint_update:ComplaintUpdateBase,db: SessionLocal = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    return give_complaint_updates(complaint_update,db, current_user)

# @router.post("{complaint_id}/comment", response_model= CommentResponse)
# async def comment(complaint_id:int, comment:CommentCreate,db: SessionLocal = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
#     return create_comment(db, complaint_id, comment, current_user)
