from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Many-to-Many Relationship Table
rezept_tags = Table(
    'rezept_tags',
    Base.metadata,
    Column('rezept_id', Integer, ForeignKey('rezepte.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Rezept(Base):
    __tablename__ = "rezepte"
    
    id = Column(Integer, primary_key=True, index=True)
    titel = Column(String(255), nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    zutaten = Column(Text, nullable=False)
    zubereitung = Column(Text, nullable=False)
    bild_url = Column(String(500), nullable=True)
    portionen = Column(String(50), nullable=True)
    zubereitungszeit = Column(String(50), nullable=True)
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    
    # Relationship zu Tags
    tags = relationship("Tag", secondary=rezept_tags, back_populates="rezepte")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    # Relationship zu Rezepten
    rezepte = relationship("Rezept", secondary=rezept_tags, back_populates="tags")