from recipe_scrapers import scrape_html
import requests
from typing import Dict, List, Optional
import re

class RezeptScraper:
    
    @staticmethod
    def scrape_rezept(url: str) -> Dict:
        """
        Scraped ein Rezept von der gegebenen URL
        """
        try:
            # HTML von der URL holen
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            # Rezept scrapen
            scraper = scrape_html(html=response.content, org_url=url)
            
            # Zutaten als Liste mit Zeilenumbrüchen
            zutaten_liste = scraper.ingredients()
            zutaten = "\n".join(zutaten_liste)
            
            # Zubereitung
            zubereitung = scraper.instructions()
            
            # Zeitangaben extrahieren
            zubereitungszeit = None
            if scraper.total_time():
                zubereitungszeit = f"{scraper.total_time()} Minuten"
            
            # Portionen
            portionen = None
            if scraper.yields():
                portionen = scraper.yields()
            
            rezept_data = {
                "titel": scraper.title(),
                "url": url,
                "zutaten": zutaten,
                "zubereitung": zubereitung,
                "bild_url": scraper.image() if scraper.image() else None,
                "portionen": portionen,
                "zubereitungszeit": zubereitungszeit
            }
            
            return rezept_data
            
        except Exception as e:
            raise Exception(f"Fehler beim Scrapen: {str(e)}")
    
    @staticmethod
    def auto_tag_rezept(zutaten: str, zubereitung: str, zubereitungszeit: Optional[str]) -> List[str]:
        """
        Erstellt automatisch Tags basierend auf Inhalt
        """
        tags = []
        text = (zutaten + " " + zubereitung).lower()
        
        # Vegetarisch/Vegan Check
        fleisch_keywords = ['fleisch', 'hähnchen', 'rind', 'schwein', 'lamm', 'fisch', 'lachs', 'thunfisch', 'garnelen']
        if not any(keyword in text for keyword in fleisch_keywords):
            tags.append("vegetarisch")
        
        vegan_keywords = ['milch', 'butter', 'käse', 'sahne', 'ei', 'eier', 'joghurt', 'quark']
        if not any(keyword in text for keyword in vegan_keywords) and 'vegetarisch' in tags:
            tags.append("vegan")
        
        # Schnelle Rezepte
        if zubereitungszeit:
            minuten = re.findall(r'\d+', zubereitungszeit)
            if minuten and int(minuten[0]) <= 30:
                tags.append("schnell")
        
        # Backwaren
        if any(keyword in text for keyword in ['backen', 'ofen', 'kuchen', 'teig']):
            tags.append("backen")
        
        # Gesund
        if any(keyword in text for keyword in ['vollkorn', 'gemüse', 'salat', 'quinoa', 'tofu']):
            tags.append("gesund")
        
        # Comfort Food
        if any(keyword in text for keyword in ['pasta', 'pizza', 'burger', 'auflauf', 'suppe']):
            tags.append("comfort-food")
        
        return tags