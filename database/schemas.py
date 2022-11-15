from datetime import datetime
from typing import Union

from pydantic import BaseModel, EmailStr, Field


class PostBase(BaseModel):
    title: str
    description: Union[str, None] = None
    

class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: EmailStr
    


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    # posts: list[Post] = []

    class Config:
        orm_mode = True

class UserProfileBaseSchema(BaseModel):
    first_name: str
    last_name: str
    phone_number: str = Field(regex=r'(^$|^[789](\d{9}|\d{10})$)')
    profile_picture: str
    ward: int

    class Config:
        orm_mode = True

class UserProfileSchema(UserProfileBaseSchema):
    municipality: int
    district: int
    username: str
    email: EmailStr
    ward_slug: str
    municipality_name: str
    district_name: str
    ward_name: str
    total_completed_complaints: int
    total_pending_complaints: int
    

class UpdatedProfileSchema(UserProfileBaseSchema):
    municipality: int
    district: int
    username: str

class MessageWithStatus(BaseModel):
    status_code: int
    content: dict

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class FirstValues(BaseModel):
    district_id: int
    municipality_id: int
    ward_id: int

class ComplaintBase(BaseModel):
    complaint_title: str
    complaint_desc: str
    photo_url: str
    complaint_type: int
    complaint_sub_type: int
    ward_id: int

    class Config:
        orm_mode = True

class ComplaintSchema(ComplaintBase):
    id: int
    like_count: int
    dislike_count: int
    no_of_comments: int
    username: str
    completed_status: str
    created_at: datetime

class ComplaintResponseBase(ComplaintSchema):
    latitude: str
    longitude: str
    ward_slug: str

class ComplaintCreate(ComplaintBase):
    latitude: str = Field(..., regex=r'^-?([1-8]?[1-9]|[1-9]0)\.{1}\d{1,6}')
    longitude: str = Field(..., regex=r'^-?([1-8]?[1-9]|[1-9]0)\.{1}\d{1,6}')

class UpdatedComplaint(BaseModel):
    complaint_type: int
    complaint_sub_type: int
    ward_id: int
    latitude: str = Field(..., regex=r'^-?([1-8]?[1-9]|[1-9]0)\.{1}\d{1,6}')
    longitude: str = Field(..., regex=r'^-?([1-8]?[1-9]|[1-9]0)\.{1}\d{1,6}')

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    comment_text: str
    parent_comment_id: Union[int, None] = None
    class Config:
        orm_mode = True

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    username: str
    complaint_id: int
    created_at: datetime

class LikeResponse(BaseModel):
    username: str
    complaint_id: int
    like_state: str
    created_at: datetime

    class Config:
        orm_mode = True

class WardServantCreate(BaseModel):
    email: EmailStr
    temp_password: str
    password: str

class WardServantCreated(BaseModel):
    username: str
    first_name: str
    last_name: str
    qr_code: str

    class Config:
        orm_mode = True

class WardServantVerify(BaseModel):
    email: EmailStr
    password: str


class ComplaintTypeBase(BaseModel):
    type_name: str

    class Config:
        orm_mode = True

class ComplaintSubTypeBase(BaseModel):
    sub_type_name: str

    class Config:
        orm_mode = True

class ComplaintSubTypeBase(BaseModel):
    sub_type_name: str

    class Config:
        orm_mode = True

class ProfilePicture(BaseModel):
    profile_picture: str

    class Config:
        orm_mode = True

class ComplaintListResponse(BaseModel):
    Complaint: ComplaintSchema
    ComplaintType : ComplaintTypeBase
    UserProfile: ProfilePicture

class ComplaintResponse(BaseModel):
    Complaint: ComplaintResponseBase
    ComplaintType : ComplaintTypeBase
    ComplaintSubType : ComplaintSubTypeBase
    UserProfile: ProfilePicture

class WardBase(BaseModel):
    ward_name: str
    ward_slug: str

    class Config:
        orm_mode = True

class UserComplaintsBase(BaseModel):
    complaint_title: str
    complaint_desc: str
    id: int
    complaint_type: int
    complaint_sub_type: int
    completed_status: str
    ward_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserComplaintsResponse(BaseModel):
    Complaint: UserComplaintsBase
    Ward: WardBase

    class Config:
        orm_mode = True

class VoteResponse(BaseModel):
    complaint_id: int
    vote: int
    # username: str

    class Config:
        orm_mode = True

class ComplaintUpdateBase(BaseModel):
    complaint_id: int
    update_text: str

class ComplaintUpdateResponse(ComplaintUpdateBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CouncillorBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    profile_picture: str
    position: str

    class Config:
        orm_mode = True
