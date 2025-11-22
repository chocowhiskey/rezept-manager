const API_URL = 'http://localhost:8000';

// Check if already logged in
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (token) {
        // Redirect to main app
        window.location.href = 'index.html';
    }
});

// Show Login Form
function showLogin() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('message').style.display = 'none';
}

// Show Register Form
function showRegister() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
    document.getElementById('message').style.display = 'none';
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    const btnText = document.getElementById('loginBtnText');
    const loader = document.getElementById('loginLoader');
    const btn = event.target.querySelector('button');
    
    // Show loader
    btn.disabled = true;
    btnText.style.display = 'none';
    loader.style.display = 'inline-block';
    
    try {
        // Login request mit FormData (OAuth2 Format)
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login fehlgeschlagen');
        }
        
        const data = await response.json();
        
        // Token speichern
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('username', username);
        
        showMessage('✅ Login erfolgreich! Weiterleitung...', 'success');
        
        // Redirect to main app
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);
        
    } catch (error) {
        showMessage(`❌ ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
}

// Handle Register
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const btnText = document.getElementById('registerBtnText');
    const loader = document.getElementById('registerLoader');
    const btn = event.target.querySelector('button');
    
    // Show loader
    btn.disabled = true;
    btnText.style.display = 'none';
    loader.style.display = 'inline-block';
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registrierung fehlgeschlagen');
        }
        
        showMessage('✅ Registrierung erfolgreich! Du kannst dich jetzt einloggen.', 'success');
        
        // Switch to login form after 2 seconds
        setTimeout(() => {
            showLogin();
            document.getElementById('loginUsername').value = username;
        }, 2000);
        
    } catch (error) {
        showMessage(`❌ ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
}

// Show Message
function showMessage(text, type) {
    const message = document.getElementById('message');
    message.textContent = text;
    message.className = `message ${type}`;
    
    if (type === 'error') {
        setTimeout(() => {
            message.style.display = 'none';
        }, 5000);
    }
}