from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from requests import Session

from database.db import engine
from database.dependency import get_db
from database.models import (Base, ComplaintSubType, ComplaintType, District,
                             Municipality, Ward)
from database.schemas import UserBase
from governance_routers.auth_router import auth as auth_router
from governance_routers.councillor import councillor_router
from router.auth import auth
from router.auth.auth_functions import get_current_active_user
from router.complaints import complaints_router
from router.users import users_router
from router.ward import ward_routes

# creates initial database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()#docs_url=None, redoc_url=None,openapi_url=None)

# @app.on_event("startup")
# async def startup():
#     create_zones_csv()


origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth.router,
    )
app.include_router(
    users_router.router
    )

app.include_router(
    complaints_router.router
    )

app.include_router(
    ward_routes.router
    )

authority = FastAPI()

authority.include_router(
    auth_router.router,
    )

authority.include_router(
    councillor_router.router
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/validatelogin", response_model=str)
async def validate_login(current_user: UserBase = Depends(get_current_active_user)):
    return current_user.username

@authority.get("/sub")
def read_sub():
    return {"message": "Hello World from sub API"}

zone = FastAPI()
@zone.get("/districts_and_complaint_types")
def read_districts_and_complaints(db:Session = Depends(get_db)):
    districts = db.query(District).all()
    complaints_types = db.query(ComplaintType).all()
    return {"districts":districts, "complaints_types":complaints_types}

@zone.get("/municipalities/{district_id}")
def read_municipalities(district_id:int, db:Session = Depends(get_db)):
    municipalities = db.query(Municipality).filter(
        Municipality.district_id == district_id
    ).all()
    return municipalities

@zone.get("/wards/{municipality_id}")
def read_wards(municipality_id:int,db:Session = Depends(get_db)):
    wards = db.query(Ward).filter(
        Ward.municipality_id == municipality_id
    ).all()
    return wards

@zone.get("/districts")
def read_districts(db:Session = Depends(get_db)):
    districts = db.query(District).all()
    return districts

@zone.get("/complaint_subtypes/{complaint_id}")
def read_subcomplaints(complaint_id:int,db:Session = Depends(get_db)):
    subcomplaints = db.query(ComplaintSubType).filter(
        ComplaintSubType.parent_type == complaint_id
    ).all()
    return subcomplaints

app.mount("/authority", authority)
app.mount("/zone", zone)


