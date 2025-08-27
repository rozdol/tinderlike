// Admin Dashboard JavaScript
const API_BASE_URL = 'http://localhost:8000/api/v1';
let currentAdmin = null;
let editingOfferId = null;

// Initialize admin dashboard
document.addEventListener('DOMContentLoaded', function() {
    checkAdminAuth();
    setupEventListeners();
});

// Check if user is admin and load data
async function checkAdminAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            currentAdmin = await response.json();
            if (!currentAdmin.is_admin) {
                alert('Access denied. Admin privileges required.');
                window.location.href = 'index.html';
                return;
            }
            
            document.getElementById('admin-info').textContent = 
                `Welcome, ${currentAdmin.full_name || currentAdmin.email}`;
            
            // Load initial data
            loadDashboardStats();
            loadUsers();
            loadOffers();
            loadActions();
        } else {
            localStorage.removeItem('access_token');
            window.location.href = 'index.html';
        }
    } catch (error) {
        console.error('Error checking admin auth:', error);
        window.location.href = 'index.html';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Search and filter listeners
    document.getElementById('user-search').addEventListener('input', debounce(filterUsers, 300));
    document.getElementById('user-filter').addEventListener('change', filterUsers);
    document.getElementById('offer-search').addEventListener('input', debounce(filterOffers, 300));
    document.getElementById('offer-filter').addEventListener('change', filterOffers);
    document.getElementById('action-filter').addEventListener('change', filterActions);
    
    // Form submissions
    document.getElementById('offer-form').addEventListener('submit', handleOfferSubmit);
    document.getElementById('user-form').addEventListener('submit', handleUserSubmit);
}

// Navigation
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.admin-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(`${sectionName}-section`).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Dashboard Functions
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });

        if (response.ok) {
            const stats = await response.json();
            updateStatsDisplay(stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateStatsDisplay(stats) {
    document.getElementById('total-users').textContent = stats.total_users;
    document.getElementById('total-offers').textContent = stats.total_offers;
    document.getElementById('total-likes').textContent = stats.total_likes;
    document.getElementById('total-dislikes').textContent = stats.total_dislikes;
    document.getElementById('active-offers').textContent = stats.active_offers;
    document.getElementById('verified-users').textContent = stats.verified_users;
}

function refreshStats() {
    loadDashboardStats();
}

// User Management Functions
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });

        if (response.ok) {
            const users = await response.json();
            displayUsers(users);
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function displayUsers(users) {
    const tbody = document.getElementById('users-tbody');
    tbody.innerHTML = '';

    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="loading">No users found</td></tr>';
        return;
    }

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.full_name || 'N/A'}</td>
            <td>${user.email}</td>
            <td>${user.phone}</td>
            <td>
                <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                    ${user.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <span class="status-badge ${user.is_admin ? 'admin' : 'user'}">
                    ${user.is_admin ? 'Admin' : 'User'}
                </span>
            </td>
            <td>${new Date(user.created_at).toLocaleDateString()}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    ${!user.is_admin ? `
                        <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    ` : ''}
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function filterUsers() {
    const search = document.getElementById('user-search').value;
    const filter = document.getElementById('user-filter').value;
    
    let url = `${API_BASE_URL}/admin/users?`;
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (filter !== '') url += `is_admin=${filter}`;
    
    fetch(url, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
    })
    .then(response => response.json())
    .then(users => displayUsers(users))
    .catch(error => console.error('Error filtering users:', error));
}

function refreshUsers() {
    loadUsers();
}

// Offer Management Functions
async function loadOffers() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/offers`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });

        if (response.ok) {
            const offers = await response.json();
            displayOffers(offers);
        }
    } catch (error) {
        console.error('Error loading offers:', error);
    }
}

function displayOffers(offers) {
    const tbody = document.getElementById('offers-tbody');
    tbody.innerHTML = '';

    if (offers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="loading">No offers found</td></tr>';
        return;
    }

    offers.forEach(offer => {
        const discountText = offer.discount_percentage 
            ? `${offer.discount_percentage}% off`
            : offer.discount_amount 
                ? `$${offer.discount_amount} off`
                : 'No discount';
        
        const expiryClass = offer.time_until_expiry === 'Expired' ? 'expired' : 
                           offer.time_until_expiry.includes('h') || offer.time_until_expiry.includes('m') ? 'expiring-soon' : '';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${offer.id}</td>
            <td>${offer.title}</td>
            <td>${offer.provider_name}</td>
            <td>
                <span class="category-badge ${offer.category}">
                    ${offer.category}
                </span>
            </td>
            <td>${discountText}</td>
            <td>
                <span class="status-badge ${offer.is_active ? 'active' : 'inactive'}">
                    ${offer.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <span class="expiry-time ${expiryClass}">
                    ${offer.time_until_expiry}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="editOffer(${offer.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteOffer(${offer.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function filterOffers() {
    const search = document.getElementById('offer-search').value;
    const filter = document.getElementById('offer-filter').value;
    
    let url = `${API_BASE_URL}/admin/offers?`;
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (filter !== '') url += `is_active=${filter}`;
    
    fetch(url, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
    })
    .then(response => response.json())
    .then(offers => displayOffers(offers))
    .catch(error => console.error('Error filtering offers:', error));
}

function refreshOffers() {
    loadOffers();
}

// Actions Log Functions
async function loadActions() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/actions`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });

        if (response.ok) {
            const actions = await response.json();
            displayActions(actions);
        }
    } catch (error) {
        console.error('Error loading actions:', error);
    }
}

function displayActions(actions) {
    const tbody = document.getElementById('actions-tbody');
    tbody.innerHTML = '';

    if (actions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No actions found</td></tr>';
        return;
    }

    actions.forEach(action => {
        const details = action.details ? JSON.parse(action.details) : {};
        const detailsText = Object.entries(details)
            .map(([key, value]) => `${key}: ${value}`)
            .join(', ');

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${action.id}</td>
            <td>${action.admin_user?.full_name || action.admin_user?.email || 'Unknown'}</td>
            <td>
                <span class="status-badge ${action.action_type}">
                    ${action.action_type}
                </span>
            </td>
            <td>${action.resource_type} #${action.resource_id}</td>
            <td>${detailsText || 'No details'}</td>
            <td>${new Date(action.created_at).toLocaleString()}</td>
        `;
        tbody.appendChild(row);
    });
}

function filterActions() {
    const filter = document.getElementById('action-filter').value;
    
    let url = `${API_BASE_URL}/admin/actions`;
    if (filter) url += `?action_type=${filter}`;
    
    fetch(url, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
    })
    .then(response => response.json())
    .then(actions => displayActions(actions))
    .catch(error => console.error('Error filtering actions:', error));
}

function refreshActions() {
    loadActions();
}

// Modal Functions
function showCreateOfferModal() {
    editingOfferId = null;
    document.getElementById('offer-modal-title').textContent = 'Create New Offer';
    document.getElementById('offer-submit-btn').textContent = 'Create Offer';
    document.getElementById('offer-form').reset();
    showModal('offer-modal');
}

function editOffer(offerId) {
    editingOfferId = offerId;
    document.getElementById('offer-modal-title').textContent = 'Edit Offer';
    document.getElementById('offer-submit-btn').textContent = 'Update Offer';
    
    // Load offer data
    fetch(`${API_BASE_URL}/admin/offers/${offerId}`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
    })
    .then(response => response.json())
    .then(offer => {
        document.getElementById('offer-title').value = offer.title;
        document.getElementById('offer-provider').value = offer.provider_name;
        document.getElementById('offer-description').value = offer.description || '';
        document.getElementById('offer-category').value = offer.category;
        document.getElementById('offer-image').value = offer.image_url || '';
        document.getElementById('offer-original-price').value = offer.original_price || '';
        document.getElementById('offer-discounted-price').value = offer.discounted_price || '';
        document.getElementById('offer-discount-percent').value = offer.discount_percentage || '';
        document.getElementById('offer-discount-amount').value = offer.discount_amount || '';
        document.getElementById('offer-referral-link').value = offer.referral_link || '';
        document.getElementById('offer-promo-code').value = offer.promo_code || '';
        document.getElementById('offer-instructions').value = offer.instructions || '';
        document.getElementById('offer-terms').value = offer.terms_conditions || '';
        document.getElementById('offer-expiry').value = formatDateTimeForInput(offer.expiry_date);
        document.getElementById('offer-status').value = offer.is_active.toString();
        
        showModal('offer-modal');
    })
    .catch(error => console.error('Error loading offer:', error));
}

function closeOfferModal() {
    hideModal('offer-modal');
    editingOfferId = null;
}

async function handleOfferSubmit(event) {
    event.preventDefault();
    
    const formData = {
        title: document.getElementById('offer-title').value,
        provider_name: document.getElementById('offer-provider').value,
        description: document.getElementById('offer-description').value,
        category: document.getElementById('offer-category').value,
        image_url: document.getElementById('offer-image').value,
        original_price: parseFloat(document.getElementById('offer-original-price').value) || null,
        discounted_price: parseFloat(document.getElementById('offer-discounted-price').value) || null,
        discount_percentage: parseFloat(document.getElementById('offer-discount-percent').value) || null,
        discount_amount: parseFloat(document.getElementById('offer-discount-amount').value) || null,
        referral_link: document.getElementById('offer-referral-link').value,
        promo_code: document.getElementById('offer-promo-code').value,
        instructions: document.getElementById('offer-instructions').value,
        terms_conditions: document.getElementById('offer-terms').value,
        expiry_date: new Date(document.getElementById('offer-expiry').value).toISOString(),
        is_active: document.getElementById('offer-status').value === 'true'
    };

    const url = editingOfferId 
        ? `${API_BASE_URL}/admin/offers/${editingOfferId}`
        : `${API_BASE_URL}/admin/offers`;
    
    const method = editingOfferId ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            closeOfferModal();
            loadOffers();
            alert(editingOfferId ? 'Offer updated successfully!' : 'Offer created successfully!');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error saving offer:', error);
        alert('Error saving offer');
    }
}

function editUser(userId) {
    // Load user data
    fetch(`${API_BASE_URL}/admin/users/${userId}`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
    })
    .then(response => response.json())
    .then(user => {
        document.getElementById('edit-user-id').value = user.id;
        document.getElementById('edit-user-name').value = user.full_name || '';
        document.getElementById('edit-user-username').value = user.username || '';
        document.getElementById('edit-user-email').value = user.email;
        document.getElementById('edit-user-phone').value = user.phone;
        document.getElementById('edit-user-status').value = user.is_active.toString();
        document.getElementById('edit-user-admin').value = user.is_admin.toString();
        document.getElementById('edit-user-email-verified').value = user.email_verified.toString();
        document.getElementById('edit-user-phone-verified').value = user.phone_verified.toString();
        
        showModal('user-modal');
    })
    .catch(error => console.error('Error loading user:', error));
}

function closeUserModal() {
    hideModal('user-modal');
}

async function handleUserSubmit(event) {
    event.preventDefault();
    
    const userId = document.getElementById('edit-user-id').value;
    const formData = {
        full_name: document.getElementById('edit-user-name').value,
        username: document.getElementById('edit-user-username').value,
        is_active: document.getElementById('edit-user-status').value === 'true',
        is_admin: document.getElementById('edit-user-admin').value === 'true',
        email_verified: document.getElementById('edit-user-email-verified').value === 'true',
        phone_verified: document.getElementById('edit-user-phone-verified').value === 'true'
    };

    try {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            closeUserModal();
            loadUsers();
            alert('User updated successfully!');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error updating user:', error);
        alert('Error updating user');
    }
}

// Delete Functions
async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });

        if (response.ok) {
            loadUsers();
            alert('User deleted successfully!');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Error deleting user');
    }
}

async function deleteOffer(offerId) {
    if (!confirm('Are you sure you want to delete this offer? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/admin/offers/${offerId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });

        if (response.ok) {
            loadOffers();
            alert('Offer deleted successfully!');
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error deleting offer:', error);
        alert('Error deleting offer');
    }
}

// Utility Functions
function showModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function formatDateTimeForInput(dateString) {
    const date = new Date(dateString);
    return date.toISOString().slice(0, 16);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function goToMainApp() {
    window.location.href = 'index.html';
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = 'index.html';
}
