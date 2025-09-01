// frontend/js/app.js
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Check if user is logged in
function checkAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    
    if (token && user) {
        document.getElementById('login-link').style.display = 'none';
        document.getElementById('register-link').style.display = 'none';
        document.getElementById('profile-link').style.display = 'inline-block';
        document.getElementById('logout-link').style.display = 'inline-block';
        
        if (user.role === 'teacher') {
            // Show teacher-specific features
            const teacherNav = document.createElement('li');
            teacherNav.innerHTML = `<a href="teacher.html">Teacher Portal</a>`;
            document.querySelector('nav ul').insertBefore(teacherNav, document.getElementById('profile-link'));
        }
    } else {
        document.getElementById('login-link').style.display = 'inline-block';
        document.getElementById('register-link').style.display = 'inline-block';
        document.getElementById('profile-link').style.display = 'none';
        document.getElementById('logout-link').style.display = 'none';
    }
}

// Show login modal
function showLogin() {
    document.getElementById('login-modal').style.display = 'block';
}

// Show register modal
function showRegister() {
    document.getElementById('register-modal').style.display = 'block';
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Handle login form submission
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            closeModal('login-modal');
            checkAuth();
            alert('Login successful!');
            
            // Redirect based on role
            if (data.user.role === 'teacher') {
                window.location.href = 'teacher.html';
            } else {
                window.location.href = 'student.html';
            }
        } else {
            const error = await response.json();
            alert(`Login failed: ${error.detail}`);
        }
    } catch (error) {
        alert('Login failed. Please try again.');
    }
});

// Handle register form submission
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userData = {
        username: document.getElementById('register-username').value,
        email: document.getElementById('register-email').value,
        password: document.getElementById('register-password').value,
        role: document.getElementById('register-role').value,
        phone_number: document.getElementById('register-phone').value || null,
        country: document.getElementById('register-country').value || null,
        language_preference: 'en'
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            closeModal('register-modal');
            alert('Registration successful! Please login.');
            showLogin();
        } else {
            const error = await response.json();
            alert(`Registration failed: ${error.detail}`);
        }
    } catch (error) {
        alert('Registration failed. Please try again.');
    }
});

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    checkAuth();
    window.location.href = 'index.html';
}

// Load featured resources
async function loadFeaturedResources() {
    try {
        const response = await fetch(`${API_BASE_URL}/resources/?limit=6`);
        if (response.ok) {
            const resources = await response.json();
            const resourcesContainer = document.getElementById('featured-resources');
            
            resourcesContainer.innerHTML = resources.map(resource => `
                <div class="resource-card">
                    <div class="resource-content">
                        <h3 class="resource-title">${resource.title}</h3>
                        <p class="resource-description">${resource.description || 'No description available'}</p>
                        <div class="resource-meta">
                            <span>${resource.subject} • ${resource.grade_level}</span>
                            <span>${resource.view_count} views</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load resources:', error);
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadFeaturedResources();
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        const modals = document.getElementsByClassName('modal');
        for (let modal of modals) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        }
    });
});