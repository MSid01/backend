from database.crud import get_ward
from database.models import (Comment, Complaint, ComplaintStatus,
                             ComplaintSubType, ComplaintType, ComplaintUpdate,
                             UserProfile, Votes, Ward, WardServantProfile)
from database.schemas import (CommentCreate, ComplaintCreate, UpdatedComplaint,
                              UserBase)
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


def get_complaints(db: Session, skip: int = 0, limit: int = 30, ward_slug: str='',recent: bool = False,resolved: bool = False):#-> List[ComplaintBase]:
    ward = db.query(Ward).filter(Ward.ward_slug == ward_slug).first()
    if not ward:
        raise HTTPException(status_code=404, detail="Complaints Not found")
    if recent:
        complaints = db.query(Complaint, ComplaintType, UserProfile).filter(Complaint.ward_id==ward.ward_id, Complaint.complaint_type==ComplaintType.id, UserProfile.username==Complaint.username, Complaint.completed_status=="PENDING").order_by(Complaint.created_at.desc()).offset(skip).limit(limit).all()
    elif resolved:
        complaints = db.query(Complaint, ComplaintType, UserProfile).filter(Complaint.ward_id == ward.ward_id, Complaint.complaint_type==ComplaintType.id, UserProfile.username==Complaint.username, Complaint.completed_status=="COMPLETED").offset(skip).limit(limit).all()
    else: 
        complaints = db.query(Complaint, ComplaintType, UserProfile).filter(Complaint.ward_id == ward.ward_id, Complaint.complaint_type==ComplaintType.id, UserProfile.username==Complaint.username, Complaint.completed_status=="PENDING").order_by(Complaint.like_count.desc()).offset(skip).limit(limit).all()
    return complaints

def get_complaint(db:Session, ward_slug:str = '', complaint_id:int = 0 ):
    ward = db.query(Ward).filter(Ward.ward_slug == ward_slug).first()
    if not ward:
        raise HTTPException(status_code=404, detail="Complaint Not found")
    complaint = db.query(Complaint, ComplaintType, ComplaintSubType, UserProfile).filter(Complaint.id==complaint_id, Complaint.complaint_type==ComplaintType.id, Complaint.complaint_sub_type==ComplaintSubType.id, UserProfile.username==Complaint.username).first()
    complaint.Complaint.ward_slug = ward_slug
    return complaint

async def reform_complaint(db: Session, complaint: UpdatedComplaint, current_user: UserBase, complaint_id: int):
    db_complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint Not found")
    if db_complaint.username != current_user.username:
        raise HTTPException(status_code=401, detail="Not Authorized")
    try:
        db_complaint.complaint_type = complaint.complaint_type
        db_complaint.complaint_sub_type = complaint.complaint_sub_type
        db_complaint.ward_id = complaint.ward_id
        db_complaint.latitude = complaint.latitude
        db_complaint.longitude = complaint.longitude

        ward_servant = db.query(WardServantProfile).filter(WardServantProfile.ward_id == complaint.ward_id, WardServantProfile.position == "NAGARSEVAK").first() 
        if not ward_servant:
            raise HTTPException(status_code=404, detail="No ward servant found")
        db_complaint_status = db.query(ComplaintStatus).filter(ComplaintStatus.complaint_id == complaint_id).first()
        db_complaint_status.ward_servant_username = ward_servant.username
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Complaint updated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str("Internal server error"))

async def reform_complaint_status(db: Session, complaint_id: int, current_user: UserBase):
    db_complaint = db.query(Complaint).filter(Complaint.id == complaint_id, Complaint.username == current_user.username).first()
    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint Not found")
    if(db_complaint.completed_status == "COMPLETED"):
        raise HTTPException(status_code=400, detail="Complaint already resolved")
    try:
        db_complaint.completed_status = "COMPLETED"
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Complaint Resolved"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str("Internal server error"))

async def create_complaint(db: Session, complaint: ComplaintCreate, current_user: UserBase):
    ward_servant = db.query(WardServantProfile).filter(WardServantProfile.ward_id == complaint.ward_id, WardServantProfile.position == "NAGARSEVAK").first() #Hard coded for now
    if not ward_servant:
        raise HTTPException(status_code=404, detail="No ward servant found")
    try:
        db_complaint = Complaint( **complaint.dict(), username=current_user.username)
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)
        db_complaint_status = ComplaintStatus(
            complaint_id=db_complaint.id,
            ward_servant_username=ward_servant.username,
            completed_status="PENDING",
        )
        db.add(db_complaint_status)
        db.commit()
        db.refresh(db_complaint_status)
        db_complaint.ward_slug = get_ward(db, complaint.ward_id).ward_slug
        return db_complaint
    except Exception as e:
        raise HTTPException(status_code=500, detail=str("Internal server error"))

def get_comments(db: Session, complaint_id: int,parent_comment_id):
    comments = db.query(Comment).filter(Comment.complaint_id == complaint_id,  Comment.parent_comment_id==parent_comment_id).all()
    return comments

def create_comment(db: Session, complaint_id: int, comment: CommentCreate, current_user: UserBase):
    try:
        db_comment = Comment( 
            comment_text=comment.comment_text, 
            parent_comment_id=comment.parent_comment_id,
            complaint_id=complaint_id, 
            username=current_user.username)
        db.query(Complaint).filter(Complaint.id == complaint_id).update({Complaint.no_of_comments: Complaint.no_of_comments + 1})
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str("Internal server error"))

def get_vote_count(db: Session, complaint_id: int):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint Not found")
    return complaint.like_count

def create_post_vote(db:Session, complaint_id:int, vote:int, current_user: UserBase ):
    user_vote = db.query(Votes).filter(Votes.complaint_id == complaint_id, Votes.username == current_user.username).first()
    if user_vote:
        if(user_vote.vote==vote):
            return user_vote
        elif(vote==0):
            if(user_vote.vote==1):
                db.query(Complaint).filter(Complaint.id == complaint_id).update({Complaint.like_count: Complaint.like_count - 1})
            else:
                db.query(Complaint).filter(Complaint.id == complaint_id).update({Complaint.like_count: Complaint.like_count + 1})
            db.query(Votes).filter(Votes.complaint_id == complaint_id, Votes.username == current_user.username).delete()
            db.commit()
            user_vote.vote=vote
            return user_vote
        else:
            db.query(Complaint).filter(Complaint.id == complaint_id).update({Complaint.like_count: Complaint.like_count + (vote*2)})
            user_vote.vote=vote
            db.commit()
            return user_vote
    else :
        if(vote==0):
            return {
                "complaint_id":complaint_id,
                "username":current_user.username,
                "vote":vote
            }
        db_vote = Votes(complaint_id=complaint_id, username=current_user.username, vote=vote)
        db.query(Complaint).filter(Complaint.id == complaint_id).update({Complaint.like_count: Complaint.like_count + vote})
        db.add(db_vote)
        db.commit()
        db.refresh(db_vote)
        return db_vote


def get_user_votes(db: Session, username: str):
    user_votes = db.query(Votes).filter(Votes.username == username).all()
    return user_votes

def get_user_vote(db: Session, username: str, complaint_id: int):
    user_vote = db.query(Votes).filter(Votes.username == username, Votes.complaint_id == complaint_id).first()
    return user_vote

def get_complaint_updates(db: Session, complaint_id: int):
    complaint_updates = db.query(ComplaintUpdate).filter(ComplaintUpdate.complaint_id == complaint_id).order_by(ComplaintUpdate.created_at.desc()).all()
    return complaint_updates

def get_complaint_resolver(db: Session, complaint_id: int):
    complaint_resolver = db.query(ComplaintStatus).filter(ComplaintStatus.complaint_id == complaint_id).first()
    return complaint_resolver

def get_councillor(db: Session, ward_id: int):
    councillor = db.query(WardServantProfile).filter(WardServantProfile.ward_id == ward_id, WardServantProfile.position == "NAGARSEVAK").first()
    return councillor
