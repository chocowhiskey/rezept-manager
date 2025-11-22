from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    erstellt_am: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Tag Schemas
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    
    class Config:
        from_attributes = True

# Rezept Schemas
class RezeptBase(BaseModel):
    titel: str
    url: str
    zutaten: str
    zubereitung: str
    bild_url: Optional[str] = None
    portionen: Optional[str] = None
    zubereitungszeit: Optional[str] = None

class RezeptCreate(BaseModel):
    url: str

class Rezept(RezeptBase):
    id: int
    erstellt_am: datetime
    user_id: int
    owner: User  # Username wird angezeigt
    tags: List[Tag] = []
    
    class Config:
        from_attributes = True

class RezeptList(BaseModel):
    rezepte: List[Rezept]
    total: int