// frontend/js/teacher.js
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Check if user is logged in and is a teacher
function checkTeacherAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    
    if (token && user && user.role === 'teacher') {
        document.getElementById('upload-section').style.display = 'block';
        document.getElementById('my-resources').style.display = 'block';
        document.getElementById('teacher-login-prompt').style.display = 'none';
        
        document.getElementById('login-link').style.display = 'none';
        document.getElementById('register-link').style.display = 'none';
        document.getElementById('profile-link').style.display = 'inline-block';
        document.getElementById('logout-link').style.display = 'inline-block';
        
        loadTeacherResources();
    } else {
        document.getElementById('upload-section').style.display = 'none';
        document.getElementById('my-resources').style.display = 'none';
        document.getElementById('teacher-login-prompt').style.display = 'block';
    }
}

// Load teacher's resources
async function loadTeacherResources() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/resources/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const resources = await response.json();
            const resourcesContainer = document.getElementById('teacher-resources');
            
            // Filter to show only current teacher's resources
            const user = JSON.parse(localStorage.getItem('user') || 'null');
            const myResources = resources.filter(r => r.uploaded_by === user.id);
            
            resourcesContainer.innerHTML = myResources.map(resource => `
                <div class="resource-card">
                    <div class="resource-content">
                        <h3 class="resource-title">${resource.title}</h3>
                        <p class="resource-description">${resource.description || 'No description available'}</p>
                        <div class="resource-meta">
                            <span>${resource.subject} • ${resource.grade_level}</span>
                            <span>${resource.is_approved ? 'Approved' : 'Pending Approval'}</span>
                        </div>
                        <div class="resource-meta">
                            <span>${resource.view_count} views</span>
                            <button onclick="deleteResource(${resource.id})" class="btn btn-danger">Delete</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load resources:', error);
    }
}

// Handle resource upload
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const token = localStorage.getItem('token');
    const formData = new FormData();
    
    // Add all form fields to FormData
    formData.append('title', document.getElementById('resource-title').value);
    formData.append('description', document.getElementById('resource-description').value);
    formData.append('file_type', document.getElementById('resource-type').value);
    formData.append('subject', document.getElementById('resource-subject').value);
    formData.append('grade_level', document.getElementById('resource-grade').value);
    formData.append('country', document.getElementById('resource-country').value);
    formData.append('language', document.getElementById('resource-language').value);
    formData.append('tags', document.getElementById('resource-tags').value);
    
    // Add file if selected
    const fileInput = document.getElementById('resource-file');
    if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/resources/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (response.ok) {
            alert('Resource uploaded successfully! It will be available after approval.');
            document.getElementById('upload-form').reset();
            loadTeacherResources();
        } else {
            const error = await response.json();
            alert(`Upload failed: ${error.detail}`);
        }
    } catch (error) {
        alert('Upload failed. Please try again.');
    }
});

// Delete resource
async function deleteResource(resourceId) {
    if (!confirm('Are you sure you want to delete this resource?')) {
        return;
    }
    
    const token = localStorage.getItem('token');
    
    try {
        // Note: You would need to implement a DELETE endpoint in the backend
        const response = await fetch(`${API_BASE_URL}/resources/${resourceId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            alert('Resource deleted successfully!');
            loadTeacherResources();
        } else {
            const error = await response.json();
            alert(`Delete failed: ${error.detail}`);
        }
    } catch (error) {
        alert('Delete failed. Please try again.');
    }
}

// Initialize the teacher page
document.addEventListener('DOMContentLoaded', () => {
    checkTeacherAuth();
});