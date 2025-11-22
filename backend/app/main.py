from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import engine, get_db
from .scraper import RezeptScraper

# Datenbank Tables erstellen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rezept Manager API",
    description="API zum Scrapen und Verwalten von Rezepten",
    version="1.0.0"
)

# CORS für Frontend (später wichtig für Web/Mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion einschränken!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Rezept Manager API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "rezepte": "/rezepte",
            "scrape": "/rezepte/scrape"
        }
    }

@app.post("/rezepte/scrape", response_model=schemas.Rezept)
def scrape_rezept(rezept_create: schemas.RezeptCreate, db: Session = Depends(get_db)):
    """
    Scraped ein Rezept von der URL und speichert es
    """
    # Prüfen ob URL bereits existiert
    existing = db.query(models.Rezept).filter(models.Rezept.url == rezept_create.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rezept bereits vorhanden")
    
    try:
        # Rezept scrapen
        rezept_data = RezeptScraper.scrape_rezept(rezept_create.url)
        
        # Neues Rezept erstellen
        db_rezept = models.Rezept(**rezept_data)
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
def get_rezepte(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Gibt alle Rezepte zurück
    """
    rezepte = db.query(models.Rezept).offset(skip).limit(limit).all()
    return rezepte

@app.get("/rezepte/{rezept_id}", response_model=schemas.Rezept)
def get_rezept(rezept_id: int, db: Session = Depends(get_db)):
    """
    Gibt ein einzelnes Rezept zurück
    """
    rezept = db.query(models.Rezept).filter(models.Rezept.id == rezept_id).first()
    if not rezept:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    return rezept

@app.delete("/rezepte/{rezept_id}")
def delete_rezept(rezept_id: int, db: Session = Depends(get_db)):
    """
    Löscht ein Rezept
    """
    rezept = db.query(models.Rezept).filter(models.Rezept.id == rezept_id).first()
    if not rezept:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    
    db.delete(rezept)
    db.commit()
    return {"message": "Rezept gelöscht"}

@app.get("/tags", response_model=List[schemas.Tag])
def get_tags(db: Session = Depends(get_db)):
    """
    Gibt alle Tags zurück
    """
    tags = db.query(models.Tag).all()
    return tags

@app.get("/rezepte/tag/{tag_name}", response_model=List[schemas.Rezept])
def get_rezepte_by_tag(tag_name: str, db: Session = Depends(get_db)):
    """
    Filtert Rezepte nach Tag
    """
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag nicht gefunden")
    return tag.rezepte