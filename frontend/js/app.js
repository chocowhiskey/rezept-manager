const API_URL = 'http://localhost:8000';
let allRecipes = [];

// Beim Laden der Seite Rezepte laden
document.addEventListener('DOMContentLoaded', () => {
    loadRecipes();
});

// Rezept scrapen und hinzufügen
async function scrapeRecipe() {
    const urlInput = document.getElementById('recipeUrl');
    const url = urlInput.value.trim();
    const message = document.getElementById('message');
    const addBtn = document.getElementById('addBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    
    if (!url) {
        showMessage('Bitte gib eine URL ein!', 'error');
        return;
    }
    
    // Button deaktivieren und Loader anzeigen
    addBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';
    message.style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/rezepte/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Fehler beim Scrapen');
        }
        
        const recipe = await response.json();
        showMessage('✅ Rezept erfolgreich hinzugefügt!', 'success');
        urlInput.value = '';
        
        // Rezepte neu laden
        await loadRecipes();
        
    } catch (error) {
        showMessage(`❌ ${error.message}`, 'error');
    } finally {
        // Button wieder aktivieren
        addBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Alle Rezepte laden
async function loadRecipes() {
    const grid = document.getElementById('recipesGrid');
    
    try {
        const response = await fetch(`${API_URL}/rezepte`);
        allRecipes = await response.json();
        
        if (allRecipes.length === 0) {
            grid.innerHTML = '<div class="loading">Noch keine Rezepte vorhanden. Füge dein erstes Rezept hinzu! 👆</div>';
            return;
        }
        
        displayRecipes(allRecipes);
        
    } catch (error) {
        grid.innerHTML = '<div class="loading" style="color: #dc3545;">❌ Fehler beim Laden der Rezepte</div>';
        console.error(error);
    }
}

// Rezepte anzeigen
function displayRecipes(recipes) {
    const grid = document.getElementById('recipesGrid');
    
    if (recipes.length === 0) {
        grid.innerHTML = '<div class="loading">Keine Rezepte gefunden.</div>';
        return;
    }
    
    grid.innerHTML = recipes.map(recipe => `
        <div class="recipe-card" onclick="showRecipeDetails(${recipe.id})">
            ${recipe.bild_url ? 
                `<img src="${recipe.bild_url}" alt="${recipe.titel}" class="recipe-image" onerror="this.style.display='none'">` :
                '<div class="recipe-image"></div>'
            }
            <div class="recipe-content">
                <h3 class="recipe-title">${recipe.titel}</h3>
                <div class="recipe-meta">
                    ${recipe.zubereitungszeit ? `<span>⏱️ ${recipe.zubereitungszeit}</span>` : ''}
                    ${recipe.portionen ? `<span>👥 ${recipe.portionen}</span>` : ''}
                </div>
                <div class="recipe-tags">
                    ${recipe.tags.map(tag => `<span class="tag">${tag.name}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

// Nach Tag filtern
async function filterByTag(tagName) {
    // Filter Buttons aktualisieren
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    const grid = document.getElementById('recipesGrid');
    grid.innerHTML = '<div class="loading">Lade...</div>';
    
    try {
        let recipes;
        if (tagName === 'all') {
            recipes = allRecipes;
        } else {
            const response = await fetch(`${API_URL}/rezepte/tag/${tagName}`);
            recipes = await response.json();
        }
        
        displayRecipes(recipes);
        
    } catch (error) {
        grid.innerHTML = '<div class="loading" style="color: #dc3545;">Fehler beim Filtern</div>';
    }
}

// Rezept-Details im Modal anzeigen
async function showRecipeDetails(id) {
    const modal = document.getElementById('recipeModal');
    const modalBody = document.getElementById('modalBody');
    
    try {
        const response = await fetch(`${API_URL}/rezepte/${id}`);
        const recipe = await response.json();
        
        const ingredientsList = recipe.zutaten.split('\n')
            .filter(i => i.trim())
            .map(i => `<li>${i}</li>`)
            .join('');
        
        modalBody.innerHTML = `
            ${recipe.bild_url ? 
                `<img src="${recipe.bild_url}" alt="${recipe.titel}" class="modal-image" onerror="this.style.display='none'">` : 
                ''
            }
            <h2 class="modal-title">${recipe.titel}</h2>
            
            <div class="recipe-meta">
                ${recipe.zubereitungszeit ? `<span>⏱️ ${recipe.zubereitungszeit}</span>` : ''}
                ${recipe.portionen ? `<span>👥 ${recipe.portionen}</span>` : ''}
            </div>
            
            <div class="recipe-tags">
                ${recipe.tags.map(tag => `<span class="tag">${tag.name}</span>`).join('')}
            </div>
            
            <div class="modal-section">
                <h3>📝 Zutaten</h3>
                <ul class="ingredients-list">
                    ${ingredientsList}
                </ul>
            </div>
            
            <div class="modal-section">
                <h3>👨‍🍳 Zubereitung</h3>
                <div class="instructions">${recipe.zubereitung}</div>
            </div>
            
            <div class="modal-section">
                <a href="${recipe.url}" target="_blank" style="color: #667eea;">🔗 Originalrezept ansehen</a>
            </div>
            
            <button class="delete-btn" onclick="deleteRecipe(${recipe.id})">🗑️ Rezept löschen</button>
        `;
        
        modal.style.display = 'block';
        
    } catch (error) {
        console.error(error);
        alert('Fehler beim Laden des Rezepts');
    }
}

// Modal schließen
function closeModal() {
    document.getElementById('recipeModal').style.display = 'none';
}

// Modal schließen bei Klick außerhalb
window.onclick = function(event) {
    const modal = document.getElementById('recipeModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Rezept löschen
async function deleteRecipe(id) {
    if (!confirm('Möchtest du dieses Rezept wirklich löschen?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/rezepte/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            closeModal();
            showMessage('✅ Rezept gelöscht!', 'success');
            await loadRecipes();
        }
        
    } catch (error) {
        alert('Fehler beim Löschen');
    }
}

// Nachricht anzeigen
function showMessage(text, type) {
    const message = document.getElementById('message');
    message.textContent = text;
    message.className = `message ${type}`;
    
    setTimeout(() => {
        message.style.display = 'none';
    }, 5000);
}