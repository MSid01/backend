import imp

from database.db import SessionLocal
from database.dependency import get_db
from database.models import Complaint, ComplaintUpdate, WardServantProfile
from database.schemas import ComplaintUpdateBase, UserBase
from fastapi import APIRouter, Depends, HTTPException, Query
from governance_routers.auth_router.auth_functions import get_current_user


def give_complaint_updates(complaint_update: ComplaintUpdateBase,db: SessionLocal = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    ward_servant = db.query(WardServantProfile).filter(WardServantProfile.username == current_user.username).first()
    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_update.complaint_id,
        Complaint.ward_id == ward_servant.ward_id
    ).first()
    if complaint:
        complaint_updates = ComplaintUpdate(
            complaint_id = complaint.id,
            update_text = complaint_update.update_text,
            ward_servant_username = current_user.username
        )
        db.add(complaint_updates)
        db.commit()
        db.refresh(complaint_updates)
        return complaint_updates
    else:
        raise HTTPException(status_code=404, detail="Complaint not found")
