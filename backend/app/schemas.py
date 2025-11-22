from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

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
    tags: List[Tag] = []
    
    class Config:
        from_attributes = True

class RezeptList(BaseModel):
    rezepte: List[Rezept]
    total: int