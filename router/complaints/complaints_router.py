
from typing import List, Union

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.dependency import get_db
from database.schemas import (CommentCreate, CommentResponse, ComplaintCreate,
                              ComplaintListResponse, ComplaintResponse,
                              ComplaintResponseBase, ComplaintUpdateResponse,
                              CouncillorBase, MessageWithStatus,
                              UpdatedComplaint, UserBase, VoteResponse)
from router.auth.auth_functions import get_current_active_user
from router.complaints.complaints_functions import (create_comment,
                                                    create_complaint,
                                                    create_post_vote,
                                                    get_comments,
                                                    get_complaint,
                                                    get_complaint_resolver,
                                                    get_complaint_updates,
                                                    get_complaints,
                                                    get_councillor,
                                                    get_user_vote,
                                                    get_user_votes,
                                                    get_vote_count,
                                                    reform_complaint,
                                                    reform_complaint_status)

router = APIRouter(
    prefix="/complaints",
    tags=["complaints"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{ward_slug}/", response_model=List[ComplaintListResponse])
def read_complaints(ward_slug: str,skip: int = 0, limit: int = 30, recent: bool = False, resolved: bool = False, db: Session = Depends(get_db)):
    return get_complaints(db, skip, limit, ward_slug,recent,resolved )

@router.get("/{ward_slug}/{complaint_id}/", response_model=ComplaintResponse)
def read_complaint(ward_slug: str, complaint_id: int, db: Session = Depends(get_db)):
    return get_complaint(db, ward_slug, complaint_id)

@router.post("/", response_model=ComplaintResponseBase)
async def post_complaint(complaint: ComplaintCreate, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    return await create_complaint(db, complaint, current_user)

@router.patch("/{complaint_id}/")#, response_model=ComplaintResponseBase)
async def update_complaint(complaint_id: int, complaint: UpdatedComplaint, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    return await reform_complaint(db, complaint, current_user, complaint_id)

@router.patch("/{complaint_id}/update_status/", response_model=MessageWithStatus)
async def update_complaint_status(complaint_id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    return await reform_complaint_status(db,  complaint_id,current_user)

@router.get("/{complaint_id}/comments", response_model=List[CommentResponse])
def read_comments(complaint_id: int, parent_comment_id: Union[int,None] = Query(default=None), db: Session = Depends(get_db)):
    return get_comments(db, complaint_id,parent_comment_id)

@router.post("/{complaint_id}/comments/", response_model=CommentResponse)
def post_comment(comment: CommentCreate, complaint_id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    return create_comment(db, complaint_id, comment, current_user)

        

@router.post("/{complaint_id}/vote", response_model=VoteResponse)
def vote_post(complaint_id: int, vote: str=Query(default=None,regex="^(-1|0|1)$"), db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    return create_post_vote(db, complaint_id, int(vote), current_user)

@router.get("/{complaint_id}/vote", response_model=VoteResponse)
def user_vote(complaint_id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    return get_user_vote(db, current_user.username,complaint_id )

@router.get("/uservotes", response_model=List[VoteResponse])
def user_votes(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    return get_user_votes(db, current_user.username)

@router.get("/{complaint_id}/vote_count")
def vote_count(complaint_id: int, db: Session = Depends(get_db)):
    return get_vote_count(db, complaint_id)

@router.get("/{complaint_id}/complaint_updates", response_model=List[ComplaintUpdateResponse])
def complaint_updates(complaint_id: int, db: Session = Depends(get_db)):
    return get_complaint_updates(db, complaint_id)

@router.get("/{complaint_id}/complaint_resolver")
def complaint_resolver(complaint_id: int, db: Session = Depends(get_db)):
    return get_complaint_resolver(db, complaint_id)

@router.get("/{complaint_id}/councillor",response_model=CouncillorBase)
def councillor(complaint_id: int, db: Session = Depends(get_db)):
    return get_councillor(db, complaint_id)
