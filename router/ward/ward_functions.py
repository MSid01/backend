from database.models import Ward, WardServantProfile
from fastapi import HTTPException
from sqlalchemy.orm import Session


def get_ward_info(db: Session, ward_slug: str):
    ward = db.query(Ward, WardServantProfile).filter(Ward.ward_slug == ward_slug).join(WardServantProfile).first()
    if not ward:
        raise HTTPException(status_code=404, detail="Ward Not found")
    return ward
