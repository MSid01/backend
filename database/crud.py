from fastapi import Depends
from sqlalchemy.orm import Session

from database.models import (District, Municipality, TemporaryUser,
                             TemporaryWardServant, User, Ward, WardServant)


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first() 
    
def get_user_by_temp_email(db: Session, temp_email: str):
    return db.query(TemporaryUser).filter(TemporaryUser.email == temp_email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_ward_servant_by_username(db: Session, username: str):
    return db.query(WardServant).filter(WardServant.username == username).first()

def get_user_by_temp_username(db: Session, temp_username: str):
    return db.query(TemporaryUser).filter(TemporaryUser.username == temp_username).first()

def get_ward_servant_by_email(db: Session, email: str):
    return db.query(WardServant).filter(WardServant.email == email).first()

def get_ward_servant_info(db: Session, email: str):
    return db.query(TemporaryWardServant).filter(TemporaryWardServant.email == email).first()

# get district , municipality and ward id
def get_district(db: Session, district_id: int):
    return db.query(District).filter(District.district_id == district_id).first()

def get_municipality(db: Session, municipality_id: int):
    return db.query(Municipality).filter(Municipality.municipality_id == municipality_id).first()

def get_ward(db: Session, ward_id: int):
    return db.query(Ward).filter(Ward.ward_id == ward_id).first()


# get first values
def get_first_values(db:Session):
    district_id= db.query(District).first().district_id
    municipality_id= db.query(Municipality).filter(Municipality.district_id==district_id).first().municipality_id
    ward_id= db.query(Ward).filter(Ward.municipality_id==municipality_id).first().ward_id
    return {"district_id":district_id, "municipality_id": municipality_id, "ward_id": ward_id}

