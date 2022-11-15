from fastapi import APIRouter, Depends
from database.db import SessionLocal
from database.dependency import get_db
from sqlalchemy.orm import Session
from router.ward.ward_functions import get_ward_info

router = APIRouter(
    prefix="/ward",
    tags=["ward"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
def read_ward_info(ward_slug: str, db: Session = Depends(get_db)):
    return get_ward_info(db, ward_slug)
