// frontend/js/student.js
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Check if user is logged in
function checkStudentAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    
    if (token && user) {
        document.getElementById('login-link').style.display = 'none';
        document.getElementById('register-link').style.display = 'none';
        document.getElementById('profile-link').style.display = 'inline-block';
        document.getElementById('logout-link').style.display = 'inline-block';
    }
}

// Load resources based on search criteria
async function loadResources(searchParams = {}) {
    try {
        // Build query string from search parameters
        const queryParams = new URLSearchParams();
        Object.keys(searchParams).forEach(key => {
            if (searchParams[key]) {
                queryParams.append(key, searchParams[key]);
            }
        });
        
        const response = await fetch(`${API_BASE_URL}/resources/?${queryParams}`);
        if (response.ok) {
            const resources = await response.json();
            const resourcesContainer = document.getElementById('resources-list');
            
            resourcesContainer.innerHTML = resources.map(resource => `
                <div class="resource-card">
                    <div class="resource-content">
                        <h3 class="resource-title">${resource.title}</h3>
                        <p class="resource-description">${resource.description || 'No description available'}</p>
                        <div class="resource-meta">
                            <span>${resource.subject} • ${resource.grade_level}</span>
                            <span>${resource.country}</span>
                        </div>
                        <div class="resource-meta">
                            <span>${resource.view_count} views</span>
                            <button onclick="viewResource(${resource.id})" class="btn btn-primary">View Details</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load resources:', error);
    }
}

// Handle search form submission
document.getElementById('search-form').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const searchParams = {
        subject: document.getElementById('search-subject').value,
        grade_level: document.getElementById('search-grade').value,
        country: document.getElementById('search-country').value
    };
    
    // Add search query if provided
    const searchQuery = document.getElementById('search-query').value;
    if (searchQuery) {
        // Note: The backend would need to implement search functionality
        // For now, we'll just use the subject field
        searchParams.subject = searchQuery;
    }
    
    loadResources(searchParams);
});

// View resource details
function viewResource(resourceId) {
    // In a real implementation, this would show a modal or navigate to a details page
    alert(`Viewing resource ${resourceId}. This would show more details and options.`);
}

// Initialize the student page
document.addEventListener('DOMContentLoaded', () => {
    checkStudentAuth();
    loadResources(); // Load all resources initially
});