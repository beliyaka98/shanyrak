from pydantic import BaseModel

import datetime

class CommentBase(BaseModel):
    content: str

class CreateComment(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    created_at: datetime.datetime
    author_id: int
    class Config:
        orm_mode = True
        from_attributes = True

class Comments(BaseModel):
    comments: list[Comment] = []
    class Config:
        orm_mode = True
        from_attributes = True

class AdvertBase(BaseModel):
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str

class CreateAdvert(AdvertBase):
    pass

class AdvertUpdate(BaseModel):
    type: str = None
    price: int = None
    address: str = None
    area: float = None
    rooms_count: int = None
    description: str = None

class Advert(AdvertBase):
    id: int
    user_id: int
    total_comments: int
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    phone: str
    name: str
    city: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    phone: str = None
    name: str = None
    city: str = None
