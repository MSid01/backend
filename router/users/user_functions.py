# from database.crud import get_district, get_municipality, get_ward
from database.crud import get_district, get_municipality, get_ward
from database.models import Complaint, UserProfile, Ward
from database.schemas import UserBase, UserProfileBaseSchema, UserProfileSchema
from fastapi import HTTPException
from sqlalchemy.orm import Session


def get_user_profile(current_user: UserBase,db:Session)->UserProfileSchema:
    user_profile = db.query(UserProfile).filter(UserProfile.username == current_user.username).first()
    total_completed_complaints= db.query(Complaint).filter(Complaint.username == current_user.username, Complaint.completed_status == "COMPLETED").count()
    total_pending_complaints= db.query(Complaint).filter(Complaint.username == current_user.username, Complaint.completed_status == "PENDING").count()
    ward = get_ward(db, user_profile.ward)
    municipality = get_municipality(db, user_profile.municipality)
    district = get_district(db, user_profile.district)
    return UserProfileSchema(
        **user_profile.__dict__,
        email=current_user.email,
        ward_slug=ward.ward_slug,
        municipality_name = municipality.municipality_name,
        district_name = district.district_name,
        ward_name = ward.ward_name,
        total_completed_complaints=total_completed_complaints,
        total_pending_complaints=total_pending_complaints
    )

def reform_user_profile(user_profile:UserProfileBaseSchema,current_user: UserBase,db:Session):
    municipality_id = get_ward(db, user_profile.ward).municipality_id
    district_id = get_municipality(db, municipality_id).district_id
    try:
        db_user_profile =  db.query(UserProfile).filter(UserProfile.username == current_user.username).first()
        db_user_profile.first_name = user_profile.first_name
        db_user_profile.profile_picture = user_profile.profile_picture
        db_user_profile.last_name = user_profile.last_name
        db_user_profile.phone_number = user_profile.phone_number
        db_user_profile.district = district_id
        db_user_profile.municipality = municipality_id
        db_user_profile.ward = user_profile.ward
        db.commit()
        db.refresh(db_user_profile)
        return db_user_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str("Internal server error"))

def get_user_complaints(username:str, db:Session):
    complaints = db.query(Complaint, Ward).filter(Complaint.username == username, Ward.ward_id== Complaint.ward_id).all()
    return complaints
    