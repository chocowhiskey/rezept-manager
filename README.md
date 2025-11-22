# Rezept Manager

Recipe management application with automatic web scraping.

## Features (MVP)
- 🔗 Import recipes from URLs
- 📝 Automatic scraping of ingredients and instructions  
- 🏷️ Automatic tagging (vegetarian, vegan, quick, etc.)
- 🔍 Browse and search saved recipes

## Tech Stack
- **Backend**: Python, FastAPI, SQLAlchemy
- **Scraping**: recipe-scrapers (supports 100+ websites)
- **Database**: SQLite
- **Frontend**: TBD

## Setup

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API Docs: http://localhost:8000/docs

## Supported Websites
Chefkoch.de, AllRecipes, BBC Food, and 100+ more!

## Status
✅ Backend MVP complete
🚧 Frontend in progress