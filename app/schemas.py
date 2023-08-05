from pydantic import BaseModel, Field
from fastapi import Query
import datetime
from typing import Union

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

class Fadvert(BaseModel):
    id: int = Field(..., alias="_id")
    address: str

class Fadverts(BaseModel):
    shanyraks: list[Fadvert]

class Shanyrak(BaseModel):
    limit: int = Query(..., ge=1)
    offset: int = Query(..., ge=0)
    type: Union[str, None] = Query(None, regex="^(sell|rent)$")
    rooms_count: Union[int, None] = Query(None, ge=1)
    price_from: Union[int, None] = Query(None, ge=0)
    price_until: Union[int, None] = Query(None, ge=0)

class ShanyrakAdvert(BaseModel):
    id: int = Field(..., alias="_id")
    type: str
    price: int
    address: str
    area: float
    rooms_count: int

class ResponseShanyrak(BaseModel):
    total: int
    objects: list[ShanyrakAdvert]