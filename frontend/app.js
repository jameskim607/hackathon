const API_BASE_URL = 'http://localhost:8000/api/v1';

// Auth functions
function checkAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    
    if (token && user) {
        document.getElementById('login-link').style.display = 'none';
        document.getElementById('register-link').style.display = 'none';
        document.getElementById('profile-link').style.display = 'inline-block';
        document.getElementById('logout-link').style.display = 'inline-block';
        
        // Show teacher portal if teacher
        if (user.role === 'teacher' || user.role === 'admin') {
            const teacherPortal = document.getElementById('teacher-portal-link') || createTeacherPortalLink();
            teacherPortal.style.display = 'inline-block';
        }
    }
}

function createTeacherPortalLink() {
    const li = document.createElement('li');
    li.id = 'teacher-portal-link';
    li.innerHTML = '<a href="teacher.html">Teacher Portal</a>';
    document.querySelector('nav ul').appendChild(li);
    return li;
}

// Modal functions
function showLogin() {
    closeAllModals();
    document.getElementById('login-modal').style.display = 'block';
}

function showRegister() {
    closeAllModals();
    document.getElementById('register-modal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
}

// Form handlers
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    try {
        const formData = {
            username: document.getElementById('login-username').value,
            password: document.getElementById('login-password').value
        };
        
        const response = await fetch(`${API_BASE_URL}/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            closeModal('login-modal');
            checkAuth();
            showNotification('Login successful!', 'success');
            
            // Redirect based on role
            setTimeout(() => {
                if (data.user.role === 'teacher' || data.user.role === 'admin') {
                    window.location.href = 'teacher.html';
                } else {
                    window.location.href = 'student.html';
                }
            }, 1000);
            
        } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
        console.error('Login error:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Registering...';
    
    try {
        const formData = {
            username: document.getElementById('register-username').value,
            email: document.getElementById('register-email').value,
            password: document.getElementById('register-password').value,
            role: document.getElementById('register-role').value,
            phone_number: document.getElementById('register-phone').value || null,
            country: document.getElementById('register-country').value || null,
            language_preference: 'en'
        };
        
        const response = await fetch(`${API_BASE_URL}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const data = await response.json();
            showNotification('Registration successful! Please login.', 'success');
            closeModal('register-modal');
            setTimeout(() => showLogin(), 1000);
        } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
        console.error('Registration error:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
    }
});

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    checkAuth();
    showNotification('Logged out successfully', 'success');
    setTimeout(() => window.location.href = 'index.html', 1000);
}

// Load resources
async function loadFeaturedResources() {
    try {
        const response = await fetch(`${API_BASE_URL}/resources/?limit=6`);
        if (response.ok) {
            const resources = await response.json();
            const container = document.getElementById('featured-resources');
            
            if (resources.length > 0) {
                container.innerHTML = resources.map(resource => `
                    <div class="resource-card">
                        <div class="resource-content">
                            <h3 class="resource-title">${escapeHtml(resource.title)}</h3>
                            <p class="resource-description">${escapeHtml(resource.description || 'No description')}</p>
                            <div class="resource-meta">
                                <span>${escapeHtml(resource.subject)} • ${escapeHtml(resource.grade_level)}</span>
                                <span>${resource.view_count} views</span>
                            </div>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<p class="no-resources">No resources available yet. Be the first to upload!</p>';
            }
        }
    } catch (error) {
        console.error('Failed to load resources:', error);
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notif => notif.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        z-index: 1000;
        font-weight: bold;
        ${type === 'success' ? 'background: #4CAF50;' : ''}
        ${type === 'error' ? 'background: #f44336;' : ''}
        ${type === 'info' ? 'background: #2196F3;' : ''}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    loadFeaturedResources();
    
    // Close modals on outside click
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeAllModals();
        }
    });
    
    // Close modals on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
});