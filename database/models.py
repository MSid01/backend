import datetime
import random

import pyotp
from sqlalchemy import (Boolean, CheckConstraint, Column, DateTime, Enum,
                        ForeignKey, Integer, String)
from sqlalchemy.orm import relationship

from database.db import Base, SessionLocal

# district munucipality and wards


class District(Base):
    __tablename__ = "districts"
    district_id = Column(Integer, primary_key=True, index=True)
    district_name = Column(String(50), unique=True, index=True)

    municipalities = relationship("Municipality", back_populates="district")
    district_user = relationship("UserProfile", back_populates="user_district")
    
    def __repr__(self):
        return "<District(name='%s')>" % self.district_id

class Municipality(Base):
    __tablename__ = "municipalities"
    municipality_id = Column(Integer, primary_key=True, index=True)
    municipality_name = Column(String(50), unique=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.district_id"))

    district = relationship("District", back_populates="municipalities")
    wards = relationship("Ward", back_populates="municipality")
    municipality_user = relationship("UserProfile", back_populates="user_municipality")

    def __repr__(self):
        return "<Municipality(name='%s')>" % self.municipality_id

class Ward(Base):
    __tablename__ = "wards"
    ward_id = Column(Integer, primary_key=True, index=True)
    ward_slug = Column(String(50), unique=True, index=True)
    ward_name = Column(String(50), index=True)
    municipality_id = Column(Integer, ForeignKey("municipalities.municipality_id"))
    # ward_area = Column(Integer, index=True)
    # ward_population = Column(Integer, index=True)
    # no_of_police_stations = Column(Integer, index=True)
    # no_of_hospitals = Column(Integer, index=True)


    complaints = relationship("Complaint", back_populates="ward")
    municipality = relationship("Municipality", back_populates="wards")
    ward_user = relationship("UserProfile", back_populates="user_ward")
    ward_servants = relationship("WardServantProfile", back_populates="ward")
    temp_ward_servants = relationship("TemporaryWardServant", back_populates="ward")

    def __repr__(self):
        return "<Ward(name='%s')>" % self.ward_id

#WardServant model
class WardServant(Base):
    __tablename__ = "ward_servants"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    hashed_password = Column(String,index=True)
    is_active = Column(Boolean, default=True)
    secret_key = Column(String(50), index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    ward_servant_profile = relationship("WardServantProfile", back_populates="ward_servant_username", uselist = False)

    def __repr__(self):
        return "<WardServant(name='%s')>" % self.username

class TemporaryWardServant(Base):
    __tablename__ = "temporary_ward_servants"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    profile_picture = Column(String, default="")
    password = Column(String, index=True)
    phone_number = Column(String(11), index=True)
    ward_id = Column(Integer, ForeignKey("wards.ward_id"))
    position = Column(String(50), index=True, default="WARD_SERVANT")
    secret_key = Column(String(50), index=True, default = pyotp.random_base32())
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    ward = relationship("Ward", back_populates="temp_ward_servants")

    def __repr__(self):
        return "<TemporaryWardServant(name='%s')>" % self.username

class WardServantProfile(Base):
    __tablename__ = "ward_servant_profiles"
    username = Column(String(128), ForeignKey("ward_servants.username"), primary_key=True, index=True)
    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    profile_picture = Column(String, default="")
    phone_number = Column(String(11), index=True)
    ward_id = Column(Integer, ForeignKey("wards.ward_id"))
    position = Column(String(50), index=True, default="WARD_SERVANT")

    ward = relationship("Ward", back_populates="ward_servants")
    ward_servant_username = relationship("WardServant", back_populates="ward_servant_profile")
    complaint_status = relationship("ComplaintStatus", back_populates="ward_servant")
    complaint_updates = relationship("ComplaintUpdate", back_populates="ward_servant")
    def __repr__(self):
        return "<WardServant(name='%s')>" % self.id

# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128),unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    user_profile = relationship("UserProfile", uselist=False, back_populates="user_name")

    def __repr__(self):
        return "<User(name='%s')>" % self.username


class UserProfile(Base):
    __tablename__ = "user_profiles"

    username = Column(String(128), ForeignKey("users.username"), primary_key=True,index=True)
    first_name = Column(String(128),default="")
    last_name = Column(String(128),default="")
    phone_number = Column(String(11),default="")
    profile_picture = Column(String,default="https://res.cloudinary.com/sidster/image/upload/v1664633044/user_avatars/{}.png".format(random.randint(1, 100)))
    district = Column(Integer, ForeignKey("districts.district_id"), index=True,default=0)
    municipality = Column(Integer, ForeignKey("municipalities.municipality_id"), index=True, default=0)
    ward = Column(Integer, ForeignKey("wards.ward_id"), index=True, default=0)

    user_name = relationship("User", back_populates="user_profile")
    user_district = relationship("District", back_populates="district_user")
    user_municipality = relationship("Municipality", back_populates="municipality_user")
    user_ward = relationship("Ward", back_populates="ward_user")
    complaints = relationship("Complaint", back_populates="owner_username")
    comments = relationship("Comment", back_populates="user")
    votes = relationship("Votes", back_populates="user")


    def __repr__(self):
        return "<UserProfile(first_name='%s', last_name='%s')>" % (self.first_name, self.last_name)
    
# Post model

class TemporaryUser(Base):
    __tablename__ = "temporary_users"

    username = Column(String(128), primary_key= True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return "<TemporaryUser(username='%s')>" % self.username

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_title = Column(String, index=True, nullable=False)
    complaint_desc = Column(String, index=True, nullable=False)
    photo_url = Column(String, index=True,nullable=False)
    latitude = Column(String(20), index=True)
    longitude = Column(String(20), index=True)
    username = Column(String(128), ForeignKey("user_profiles.username"), index=True)
    complaint_type = Column(Integer, ForeignKey("complaint_types.id"), index=True)
    complaint_sub_type = Column(Integer, ForeignKey("complaint_sub_types.id"), index=True)
    ward_id = Column(Integer, ForeignKey("wards.ward_id"))
    completed_status = Column(String,CheckConstraint("completed_status in ('COMPLETED','PENDING')"), index=True, default="PENDING")
    like_count = Column(Integer, default=0)
    dislike_count = Column(Integer, default=0)
    no_of_comments = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)

    ward = relationship("Ward", back_populates="complaints")
    owner_username = relationship("UserProfile", back_populates="complaints")
    type = relationship("ComplaintType", back_populates="complaints")
    sub_type = relationship("ComplaintSubType", back_populates="complaints")
    comments = relationship("Comment", back_populates="complaint")
    complaint_status = relationship("ComplaintStatus", back_populates="complaint", uselist = False)
    votes = relationship("Votes", back_populates="complaint")
    complaint_updates = relationship("ComplaintUpdate", back_populates="complaint")

    def __repr__(self):
        return "<Complaint(complaint_title='%s')>" % self.complaint_title

class ComplaintType(Base):
    __tablename__ = "complaint_types"

    id = Column(Integer, primary_key=True, index= True)
    type_name = Column(String(100),unique = True, index = True)
    
    sub_complaint = relationship("ComplaintSubType", back_populates="parent_complaint")
    complaints = relationship("Complaint", back_populates="type")

    def __repr__(self):
        return "<ComplaintType(type_name='%s')>" % self.type_name

class ComplaintSubType(Base):
    __tablename__ = "complaint_sub_types"

    id = Column(Integer, primary_key=True, index= True)
    sub_type_name = Column(String(100), index = True)
    parent_type = Column(Integer, ForeignKey("complaint_types.id"), index=True)

    parent_complaint = relationship("ComplaintType", back_populates="sub_complaint")
    complaints = relationship("Complaint", back_populates="sub_type")

    def __repr__(self):
        return "<ComplaintSubType(sub_type_name='%s')>" % self.sub_type_name

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    comment_text = Column(String(160), index=True, nullable=False)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), index=True)
    username = Column(String(128), ForeignKey("user_profiles.username"), index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), index=True, default=None)

    complaint = relationship("Complaint", back_populates="comments")
    user = relationship("UserProfile", back_populates="comments")
    replies = relationship("Comment",remote_side=[id])

    def __repr__(self):
        return "<Comment(comment_text='%s')>" % self.comment_text


#Complaint Status
class ComplaintStatus(Base):
    __tablename__ = "complaint_statuses"

    complaint_id = Column(Integer, ForeignKey("complaints.id"), primary_key=True, index=True)
    ward_servant_username = Column(String(128), ForeignKey("ward_servant_profiles.username"), index=True)
    completed_status = Column(String, CheckConstraint("completed_status in ('COMPLETED','PENDING')"), index=True, default="PENDING")

    complaint = relationship("Complaint", back_populates="complaint_status")
    ward_servant = relationship("WardServantProfile", back_populates="complaint_status")


    def __repr__(self):
        return "<ComplaintStatus(status_name='%s')>" % self.status_name

class ComplaintUpdate(Base):
    __tablename__ = "complaint_updates"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), index=True)
    update_text = Column(String(160), index=True, nullable=False)
    ward_servant_username = Column(String(128), ForeignKey("ward_servant_profiles.username"), index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    complaint = relationship("Complaint", back_populates="complaint_updates")
    ward_servant = relationship("WardServantProfile", back_populates="complaint_updates")

    def __repr__(self):
        return "<ComplaintUpdates(update_text='%s')>" % self.update_text

class Votes(Base):
    __tablename__ = "votes"
    username = Column(String(128), ForeignKey("user_profiles.username"),primary_key = True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"),primary_key = True, index=True)
    vote = Column(Integer, CheckConstraint("vote in (1,0,-1)"), index=True)

    complaint = relationship("Complaint", back_populates="votes")
    user = relationship("UserProfile", back_populates="votes")

    def __repr__(self):
        return "<Votes(username='%s', complaint_id ='%s')>" %(self.username, self.complaint_id)
