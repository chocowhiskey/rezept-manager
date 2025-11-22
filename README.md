# 🍳 Rezept Manager

Recipe management application with automatic web scraping. Save recipes from any cooking website with one click!

## ✨ Features

- 🔗 **Import recipes from URLs** - Support for 100+ cooking websites
- 📝 **Automatic scraping** - Ingredients, instructions, images, cooking time
- 🏷️ **Smart auto-tagging** - Vegetarian, vegan, quick recipes, and more
- 🔍 **Filter & browse** - Easy filtering by tags
- 📱 **Responsive design** - Works on desktop and mobile
- 🎨 **Modern UI** - Beautiful gradient design with card layout

## 🛠️ Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Modern web framework
- **SQLAlchemy** - Database ORM
- **recipe-scrapers** - Scraping library (supports 100+ sites)
- **SQLite** - Database

### Frontend
- **HTML5/CSS3/JavaScript**
- **Vanilla JS** - No frameworks needed
- **Responsive design** - Mobile-first approach

## 🚀 Setup & Installation

### Backend Setup
```bash
cd backend
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

Backend runs on: http://localhost:8000  
API Docs: http://localhost:8000/docs

### Frontend Setup
```bash
cd frontend
python -m http.server 8080
```

Frontend runs on: http://localhost:8080

## 📖 Usage

1. Start both backend and frontend servers
2. Open http://localhost:8080 in your browser
3. Paste a recipe URL (e.g., from Chefkoch.de)
4. Click "Rezept hinzufügen"
5. Browse your saved recipes!

## 🌐 Supported Websites

- Chefkoch.de
- AllRecipes
- BBC Good Food
- Food Network
- And many more!

Full list: [recipe-scrapers supported sites](https://github.com/hhursev/recipe-scraper#scrapers-available-for)

## 📸 Screenshots

[Add screenshots here later]

## 🗂️ Project Structure
```
rezept-manager/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── database.py      # DB connection
│   │   └── scraper.py       # Scraping logic
│   ├── venv/
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── README.md
```

## 🎯 Roadmap / Future Features

- [ ] User authentication
- [ ] Shopping list generation
- [ ] Mobile app (React Native)
- [ ] Recipe recommendations
- [ ] Show fiber and protein content of recipes 

## 🤝 Contributing

This is a personal portfolio project, but suggestions are welcome!

## 📝 License

MIT License

## 👤 Author

[Your Name] - [Your GitHub Profile]

---

⭐ Star this repo if you find it useful!