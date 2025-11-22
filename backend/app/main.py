from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from . import models, schemas
from .database import engine, get_db
from .scraper import RezeptScraper
from .auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Datenbank Tables erstellen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rezept Manager API",
    description="API zum Scrapen und Verwalten von Rezepten mit Authentication",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Rezept Manager API with Authentication",
        "version": "2.0.0",
        "endpoints": {
            "docs": "/docs",
            "register": "/register",
            "login": "/token",
            "rezepte": "/rezepte"
        }
    }

# ===== AUTH ENDPOINTS =====

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Neuen User registrieren
    """
    # Prüfen ob Username bereits existiert
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username bereits vergeben")
    
    # Prüfen ob Email bereits existiert
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email bereits registriert")
    
    # Neuen User erstellen
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login und Token erhalten
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falscher Username oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Aktuellen User abrufen
    """
    return current_user

# ===== REZEPT ENDPOINTS (mit Auth) =====

@app.post("/rezepte/scrape", response_model=schemas.Rezept)
def scrape_rezept(
    rezept_create: schemas.RezeptCreate, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scraped ein Rezept und speichert es (Login erforderlich)
    """
    # Prüfen ob URL bereits existiert (egal von welchem User)
    existing = db.query(models.Rezept).filter(
        models.Rezept.url == rezept_create.url
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rezept bereits vorhanden")
    
    try:
        # Rezept scrapen
        rezept_data = RezeptScraper.scrape_rezept(rezept_create.url)
        
        # Neues Rezept mit user_id erstellen
        db_rezept = models.Rezept(**rezept_data, user_id=current_user.id)
        db.add(db_rezept)
        db.commit()
        db.refresh(db_rezept)
        
        # Auto-Tags generieren
        tag_names = RezeptScraper.auto_tag_rezept(
            rezept_data["zutaten"],
            rezept_data["zubereitung"],
            rezept_data.get("zubereitungszeit")
        )
        
        # Tags hinzufügen
        for tag_name in tag_names:
            tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
            if not tag:
                tag = models.Tag(name=tag_name)
                db.add(tag)
            db_rezept.tags.append(tag)
        
        db.commit()
        db.refresh(db_rezept)
        
        return db_rezept
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/rezepte", response_model=List[schemas.Rezept])
def get_rezepte(
    skip: int = 0, 
    limit: int = 100, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gibt ALLE Rezepte zurück (von allen Usern) - Login erforderlich
    """
    rezepte = db.query(models.Rezept).offset(skip).limit(limit).all()
    return rezepte

@app.get("/rezepte/{rezept_id}", response_model=schemas.Rezept)
def get_rezept(
    rezept_id: int, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gibt ein einzelnes Rezept zurück - Login erforderlich
    """
    rezept = db.query(models.Rezept).filter(
        models.Rezept.id == rezept_id
    ).first()
    if not rezept:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    return rezept

@app.delete("/rezepte/{rezept_id}")
def delete_rezept(
    rezept_id: int, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Löscht ein Rezept - Jeder eingeloggte User kann jedes Rezept löschen
    """
    rezept = db.query(models.Rezept).filter(
        models.Rezept.id == rezept_id
    ).first()
    if not rezept:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    
    db.delete(rezept)
    db.commit()
    return {"message": "Rezept gelöscht"}

@app.get("/tags", response_model=List[schemas.Tag])
def get_tags(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gibt alle Tags zurück
    """
    tags = db.query(models.Tag).all()
    return tags

@app.get("/rezepte/tag/{tag_name}", response_model=List[schemas.Rezept])
def get_rezepte_by_tag(
    tag_name: str, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Filtert ALLE Rezepte nach Tag - Login erforderlich
    """
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag nicht gefunden")
    
    return tag.rezepte