// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Global state
let currentUser = null;
let currentOffer = null;
let likedOffers = [];
let notifications = [];

// DOM Elements
const loadingScreen = document.getElementById('loading-screen');
const authContainer = document.getElementById('auth-container');
const mainApp = document.getElementById('main-app');
const loginScreen = document.getElementById('login-screen');
const registerScreen = document.getElementById('register-screen');
const verificationScreen = document.getElementById('verification-screen');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        loadUserProfile();
    } else {
        showAuth();
    }
}

function setupEventListeners() {
    // Auth forms
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('verification-form').addEventListener('submit', handleVerification);
    document.getElementById('profile-form').addEventListener('submit', handleProfileUpdate);
}

// Auth Functions
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            await loadUserProfile();
        } else {
            const error = await response.json();
            showError(error.detail || 'Login failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    } finally {
        hideLoading();
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const formData = {
        email: document.getElementById('register-email').value,
        phone: document.getElementById('register-phone').value,
        full_name: document.getElementById('register-fullname').value,
        username: document.getElementById('register-username').value || null,
    };
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });
        
        if (response.ok) {
            showVerification();
        } else {
            const error = await response.json();
            showError(error.detail || 'Registration failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    } finally {
        hideLoading();
    }
}

async function handleVerification(e) {
    e.preventDefault();
    const email = document.getElementById('register-email').value;
    const code = document.getElementById('verification-code').value;
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/auth/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, phone: document.getElementById('register-phone').value, code }),
        });
        
        if (response.ok) {
            showSuccess('Account verified successfully! Please login.');
            showLogin();
        } else {
            const error = await response.json();
            showError(error.detail || 'Verification failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    } finally {
        hideLoading();
    }
}

async function resendVerification() {
    const email = document.getElementById('register-email').value;
    const phone = document.getElementById('register-phone').value;
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/auth/resend-verification`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, phone }),
        });
        
        if (response.ok) {
            showSuccess('Verification codes sent successfully!');
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to resend codes');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    } finally {
        hideLoading();
    }
}

// OAuth Functions
async function loginWithGoogle() {
    // In a real app, you'd integrate with Google OAuth
    showError('Google OAuth integration not implemented in demo');
}

async function loginWithApple() {
    // In a real app, you'd integrate with Apple OAuth
    showError('Apple OAuth integration not implemented in demo');
}

// User Profile Functions
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });
        
        if (response.ok) {
            currentUser = await response.json();
            console.log('User profile loaded:', currentUser);
            if (currentUser.is_verified) {
                showMainApp();
                loadNextOffer();
                loadLikedOffers();
                loadNotifications();
            } else {
                showVerification();
            }
        } else {
            console.error('Failed to load user profile:', response.status);
            localStorage.removeItem('access_token');
            showAuth();
        }
    } catch (error) {
        console.error('Error loading user profile:', error);
        showAuth();
    }
}

async function handleProfileUpdate(e) {
    e.preventDefault();
    
    const formData = {
        full_name: document.getElementById('profile-fullname').value,
        username: document.getElementById('profile-username').value,
        notify_email: document.getElementById('notify-email').checked,
        notify_sms: document.getElementById('notify-sms').checked,
        notify_whatsapp: document.getElementById('notify-whatsapp').checked,
        notify_telegram: document.getElementById('notify-telegram').checked,
    };
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/users/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
            body: JSON.stringify(formData),
        });
        
        if (response.ok) {
            currentUser = await response.json();
            showSuccess('Profile updated successfully!');
            closeModal('profile-modal');
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to update profile');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    } finally {
        hideLoading();
    }
}

// Offer Functions
async function loadNextOffer() {
    try {
        const response = await fetch(`${API_BASE_URL}/offers/next`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });
        
        if (response.ok) {
            currentOffer = await response.json();
            displayOffer(currentOffer);
            showElement('swipe-area');
            hideElement('no-offers');
        } else if (response.status === 404) {
            currentOffer = null;
            showElement('no-offers');
            hideElement('swipe-area');
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to load offer');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    }
}

let countdownInterval = null;

function displayOffer(offer) {
    document.getElementById('offer-title').textContent = offer.title;
    document.getElementById('offer-description').textContent = offer.description || 'No description available';
    document.getElementById('offer-provider').textContent = offer.provider_name;
    document.getElementById('offer-category').textContent = offer.category;
    
    // Clear any existing countdown timer
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }
    
    // Start live countdown timer
    startCountdownTimer(offer.expiry_date);
    
    if (offer.image_url) {
        document.getElementById('offer-image').src = offer.image_url;
    } else {
        document.getElementById('offer-image').src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzUwIiBoZWlnaHQ9IjI1MCIgdmlld0JveD0iMCAwIDM1MCAyNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzNTAiIGhlaWdodD0iMjUwIiBmaWxsPSIjRjVGNUY1Ii8+CjxwYXRoIGQ9Ik0xNzUgMTI1QzE5MC4xODkgMTI1IDIwMi41IDEzNy4zMTEgMjAyLjUgMTUyLjVDMjAyLjUgMTY3LjY4OSAxOTAuMTg5IDE4MCAxNzUgMTgwQzE1OS44MTEgMTgwIDE0Ny41IDE2Ny42ODkgMTQ3LjUgMTUyLjVDMTQ3LjUgMTM3LjMxMSAxNTkuODExIDEyNSAxNzUgMTI1WiIgZmlsbD0iI0Q5RDlEOSIvPgo8cGF0aCBkPSJNMTc1IDEzNUMxODUuNDk3IDEzNSAxOTQgMTQzLjUwMyAxOTQgMTU0QzE5NCAxNjQuNDk3IDE4NS40OTcgMTczIDE3NSAxNzNDMTY0LjUwMyAxNzMgMTU2IDE2NC40OTcgMTU2IDE1NEMxNTYgMTQzLjUwMyAxNjQuNTAzIDEzNSAxNzUgMTM1WiIgZmlsbD0iI0M5QzlDOSIvPgo8L3N2Zz4K';
    }
    
    // Display discount information
    const discountElement = document.getElementById('offer-discount');
    if (offer.discount_percentage) {
        discountElement.innerHTML = `<span class="discount-text">${offer.discount_percentage}% OFF</span>`;
    } else if (offer.discount_amount) {
        discountElement.innerHTML = `<span class="discount-text">$${offer.discount_amount} OFF</span>`;
    } else {
        discountElement.innerHTML = `<span class="discount-text">Special Offer</span>`;
    }
}

function startCountdownTimer(expiryDate) {
    const expiryElement = document.getElementById('offer-expiry');
    const expiryTime = new Date(expiryDate).getTime();
    
    function updateCountdown() {
        const now = new Date().getTime();
        const timeLeft = expiryTime - now;
        
        if (timeLeft <= 0) {
            // Offer has expired
            expiryElement.innerHTML = '<span class="expired-text">EXPIRED</span>';
            expiryElement.className = 'offer-expiry expired';
            
            // Clear the interval
            if (countdownInterval) {
                clearInterval(countdownInterval);
                countdownInterval = null;
            }
            
            // Auto-load next offer after a short delay
            setTimeout(() => {
                loadNextOffer();
            }, 2000);
            
            return;
        }
        
        // Calculate time units
        const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
        
        // Format the countdown display
        let countdownText = '';
        let urgencyClass = '';
        
        if (days > 0) {
            countdownText = `${days.toString().padStart(2, '0')} ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            urgencyClass = 'normal';
        } else if (hours > 0) {
            countdownText = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            urgencyClass = hours < 6 ? 'urgent' : 'normal';
        } else if (minutes > 0) {
            countdownText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            urgencyClass = minutes < 30 ? 'very-urgent' : 'urgent';
        } else {
            countdownText = `${seconds.toString().padStart(2, '0')}`;
            urgencyClass = 'critical';
        }
        
        // Update the display with urgency styling
        expiryElement.innerHTML = `<span class="countdown-text">${countdownText}</span>`;
        expiryElement.className = `offer-expiry ${urgencyClass}`;
    }
    
    // Update immediately
    updateCountdown();
    
    // Update every second
    countdownInterval = setInterval(updateCountdown, 1000);
}

async function swipeOffer(action) {
    if (!currentOffer) return;
    
    // Add visual feedback immediately
    const offerCard = document.getElementById('offer-card');
    const swipeButtons = document.querySelector('.swipe-buttons');
    
    // Disable buttons during swipe
    swipeButtons.style.pointerEvents = 'none';
    
    // Add swipe animation
    if (action === 'like') {
        offerCard.style.transform = 'translateX(100px) rotate(15deg)';
        offerCard.style.opacity = '0';
    } else {
        offerCard.style.transform = 'translateX(-100px) rotate(-15deg)';
        offerCard.style.opacity = '0';
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/offers/swipe`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
            body: JSON.stringify({
                offer_id: currentOffer.id,
                action: action
            }),
        });
        
        if (response.ok) {
            if (action === 'like') {
                await loadLikedOffers();
            }
            
            // Wait a bit for the animation to complete, then load next offer
            setTimeout(() => {
                // Reset card position
                offerCard.style.transform = '';
                offerCard.style.opacity = '';
                swipeButtons.style.pointerEvents = '';
                
                // Load next offer
                loadNextOffer();
            }, 300);
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to swipe offer');
            
            // Reset card position on error
            offerCard.style.transform = '';
            offerCard.style.opacity = '';
            swipeButtons.style.pointerEvents = '';
        }
    } catch (error) {
        showError('Network error. Please try again.');
        
        // Reset card position on error
        offerCard.style.transform = '';
        offerCard.style.opacity = '';
        swipeButtons.style.pointerEvents = '';
    }
}

async function loadLikedOffers() {
    try {
        console.log('loadLikedOffers() called');
        const response = await fetch(`${API_BASE_URL}/offers/liked`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });
        
        console.log('Response status:', response.status);
        
        if (response.ok) {
            likedOffers = await response.json();
            console.log('Liked offers loaded:', likedOffers);
            updateLikedCountBadge();
            return likedOffers;
        } else {
            console.error('Failed to load liked offers:', response.status);
            return [];
        }
    } catch (error) {
        console.error('Error loading liked offers:', error);
        return [];
    }
}

function showLikedOffers() {
    console.log('showLikedOffers() called, likedOffers:', likedOffers);
    const container = document.getElementById('liked-offers-list');
    if (!container) {
        console.error('liked-offers-list container not found!');
        return;
    }
    
    container.innerHTML = '';
    
    if (likedOffers.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px 20px; color: #666;">
                <i class="fas fa-heart" style="font-size: 48px; color: #ddd; margin-bottom: 20px;"></i>
                <h3>No Liked Offers Yet</h3>
                <p>Swipe right on offers you like to see them here!</p>
            </div>
        `;
    } else {
        // Add header with count
        const header = document.createElement('div');
        header.className = 'liked-offers-header';
        header.innerHTML = `<h3>Your Liked Offers (${likedOffers.length})</h3>`;
        container.appendChild(header);
        
        likedOffers.forEach(offer => {
            const offerElement = createOfferElement(offer);
            container.appendChild(offerElement);
        });
    }
    
    console.log('Showing modal: liked-modal');
    showModal('liked-modal');
}

function createOfferElement(offer) {
    const div = document.createElement('div');
    div.className = 'offer-item';
    div.onclick = () => showOfferDetails(offer);
    
    // Format discount display
    let discountDisplay = '';
    if (offer.discount_percentage) {
        discountDisplay = `<span class="discount-badge">${offer.discount_percentage}% OFF</span>`;
    } else if (offer.discount_amount) {
        discountDisplay = `<span class="discount-badge">$${offer.discount_amount} OFF</span>`;
    } else {
        discountDisplay = `<span class="discount-badge">Special Offer</span>`;
    }
    
    div.innerHTML = `
        <div class="offer-item-content">
            <div class="offer-item-header">
                <h4>${offer.title}</h4>
                ${discountDisplay}
            </div>
            <p class="offer-description">${offer.description || 'No description available'}</p>
            <div class="offer-meta">
                <span class="provider"><i class="fas fa-building"></i> ${offer.provider_name}</span>
                <span class="category"><i class="fas fa-tag"></i> ${offer.category}</span>
                <span class="expiry"><i class="fas fa-clock"></i> ${offer.time_until_expiry}</span>
            </div>
        </div>
        <div class="offer-item-actions">
            <button class="btn-action" onclick="event.stopPropagation(); useOfferFromList('${offer.id}')">
                <i class="fas fa-external-link-alt"></i> Use Offer
            </button>
            ${offer.promo_code ? `<button class="btn-action" onclick="event.stopPropagation(); copyPromoCodeFromList('${offer.id}')">
                <i class="fas fa-copy"></i> Copy Code
            </button>` : ''}
        </div>
    `;
    
    return div;
}

// Notification Functions
async function loadNotifications() {
    try {
        const response = await fetch(`${API_BASE_URL}/notifications/unread`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });
        
        if (response.ok) {
            notifications = await response.json();
            updateNotificationBadge();
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

function updateNotificationBadge() {
    const badge = document.getElementById('notification-badge');
    if (notifications.length > 0) {
        badge.textContent = notifications.length;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function updateLikedCountBadge() {
    const badge = document.getElementById('liked-count-badge');
    if (likedOffers.length > 0) {
        badge.textContent = likedOffers.length;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function showNotifications() {
    const container = document.getElementById('notifications-list');
    container.innerHTML = '';
    
    if (notifications.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">No notifications</p>';
    } else {
        notifications.forEach(notification => {
            const notificationElement = createNotificationElement(notification);
            container.appendChild(notificationElement);
        });
    }
    
    showModal('notifications-modal');
}

function createNotificationElement(notification) {
    const div = document.createElement('div');
    div.className = `notification-item ${!notification.is_read ? 'unread' : ''}`;
    
    div.innerHTML = `
        <h4>${notification.message}</h4>
        <p>${notification.notification_type}</p>
        <div class="notification-time">${new Date(notification.sent_at).toLocaleString()}</div>
    `;
    
    return div;
}

// Modal Functions
function showModal(modalId) {
    console.log('showModal() called with modalId:', modalId);
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById(modalId);
    
    if (!overlay) {
        console.error('modal-overlay not found!');
        return;
    }
    
    if (!modal) {
        console.error(`Modal with id '${modalId}' not found!`);
        return;
    }
    
    overlay.classList.remove('hidden');
    modal.classList.remove('hidden');
    console.log('Modal should now be visible');
}

function closeModal(modalId) {
    document.getElementById('modal-overlay').classList.add('hidden');
    document.getElementById(modalId).classList.add('hidden');
}

// UI Functions
function showAuth() {
    hideLoading();
    authContainer.classList.remove('hidden');
    mainApp.classList.add('hidden');
    showLogin();
}

function showLogin() {
    loginScreen.classList.remove('hidden');
    registerScreen.classList.add('hidden');
    verificationScreen.classList.add('hidden');
}

function showRegister() {
    loginScreen.classList.add('hidden');
    registerScreen.classList.remove('hidden');
    verificationScreen.classList.add('hidden');
}

function showVerification() {
    loginScreen.classList.add('hidden');
    registerScreen.classList.add('hidden');
    verificationScreen.classList.remove('hidden');
}

function showMainApp() {
    hideLoading();
    authContainer.classList.add('hidden');
    mainApp.classList.remove('hidden');
    
    // Show admin button if user is admin
    if (currentUser && currentUser.is_admin) {
        const adminBtn = document.getElementById('admin-btn');
        if (adminBtn) {
            adminBtn.style.display = 'block';
        }
    }
}

function showLoading() {
    loadingScreen.classList.remove('hidden');
}

function hideLoading() {
    loadingScreen.classList.add('hidden');
}

function showElement(elementId) {
    document.getElementById(elementId).classList.remove('hidden');
}

function hideElement(elementId) {
    document.getElementById(elementId).classList.add('hidden');
}

function showError(message) {
    // Simple error display - you could use a toast library
    alert(message);
}

function showSuccess(message) {
    // Simple success display - you could use a toast library
    alert(message);
}

// Navigation Functions
function showOffers() {
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    event.target.closest('.nav-item').classList.add('active');
    
    // Clear any existing countdown timer
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }
    
    loadNextOffer();
}

function showLiked() {
    console.log('showLiked() called');
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    event.target.closest('.nav-item').classList.add('active');
    
    // Load fresh liked offers data
    loadLikedOffers().then((offers) => {
        console.log('Liked offers loaded:', offers);
        showLikedOffers();
    }).catch(error => {
        console.error('Error in showLiked:', error);
        // Fallback: try to show modal anyway
        showLikedOffers();
    });
}

function showProfile() {
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    event.target.closest('.nav-item').classList.add('active');
    
    // Populate profile form
    if (currentUser) {
        document.getElementById('profile-fullname').value = currentUser.full_name || '';
        document.getElementById('profile-username').value = currentUser.username || '';
        document.getElementById('profile-email').value = currentUser.email;
        document.getElementById('profile-phone').value = currentUser.phone;
        document.getElementById('notify-email').checked = currentUser.notify_email;
        document.getElementById('notify-sms').checked = currentUser.notify_sms;
        document.getElementById('notify-whatsapp').checked = currentUser.notify_whatsapp;
        document.getElementById('notify-telegram').checked = currentUser.notify_telegram;
        
        // Update verification status
        updateVerificationStatus();
    }
    
    showModal('profile-modal');
}

function updateVerificationStatus() {
    if (!currentUser) return;
    
    // Email verification status
    const emailStatusIcon = document.getElementById('email-status-icon');
    const emailStatus = document.getElementById('email-status');
    
    if (currentUser.email_verified) {
        emailStatusIcon.className = 'status-icon verified';
        emailStatus.textContent = 'Verified';
        emailStatus.className = 'status-value verified';
    } else {
        emailStatusIcon.className = 'status-icon unverified';
        emailStatus.textContent = 'Not Verified';
        emailStatus.className = 'status-value unverified';
    }
    
    // Phone verification status
    const phoneStatusIcon = document.getElementById('phone-status-icon');
    const phoneStatus = document.getElementById('phone-status');
    
    if (currentUser.phone_verified) {
        phoneStatusIcon.className = 'status-icon verified';
        phoneStatus.textContent = 'Verified';
        phoneStatus.className = 'status-value verified';
    } else {
        phoneStatusIcon.className = 'status-icon unverified';
        phoneStatus.textContent = 'Not Verified';
        phoneStatus.className = 'status-value unverified';
    }
}

function showAccountInfo() {
    if (!currentUser) return;
    
    const info = `
Account Information:
• User ID: ${currentUser.id}
• Email: ${currentUser.email}
• Phone: ${currentUser.phone}
• Account Created: ${new Date(currentUser.created_at).toLocaleDateString()}
• Last Updated: ${new Date(currentUser.updated_at).toLocaleDateString()}
• Account Status: ${currentUser.is_active ? 'Active' : 'Inactive'}
• Verification Status: ${currentUser.is_verified ? 'Verified' : 'Not Verified'}
    `;
    
    alert(info);
}

function showNotifications() {
    loadNotifications().then(() => {
        const container = document.getElementById('notifications-list');
        container.innerHTML = '';
        
        if (notifications.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666;">No notifications</p>';
        } else {
            notifications.forEach(notification => {
                const notificationElement = createNotificationElement(notification);
                container.appendChild(notificationElement);
            });
        }
        
        showModal('notifications-modal');
    });
}

// Utility Functions
function logout() {
    // Clear all data
    localStorage.removeItem('access_token');
    currentUser = null;
    currentOffer = null;
    likedOffers = [];
    notifications = [];
    
    // Clear countdown timer
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }
    
    // Close any open modals
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.add('hidden');
    });
    document.getElementById('modal-overlay').classList.add('hidden');
    
    // Show success message
    showSuccess('Logged out successfully!');
    
    // Return to auth screen
    showAuth();
}

function goToAdmin() {
    window.location.href = 'admin.html';
}

function showOfferDetails(offer) {
    const container = document.getElementById('offer-details-content');
    
    container.innerHTML = `
        <h3>${offer.title}</h3>
        <p>${offer.description || 'No description available'}</p>
        <div class="offer-details">
            <p><strong>Provider:</strong> ${offer.provider_name}</p>
            <p><strong>Category:</strong> ${offer.category}</p>
            <p><strong>Expires:</strong> ${offer.time_until_expiry}</p>
            ${offer.instructions ? `<p><strong>Instructions:</strong> ${offer.instructions}</p>` : ''}
            ${offer.terms_conditions ? `<p><strong>Terms:</strong> ${offer.terms_conditions}</p>` : ''}
        </div>
    `;
    
    showModal('offer-details-modal');
}

function useOffer() {
    const offer = currentOffer || likedOffers.find(o => o.id === currentOffer?.id);
    if (offer && offer.referral_link) {
        window.open(offer.referral_link, '_blank');
    } else {
        showError('No referral link available for this offer');
    }
    closeModal('offer-details-modal');
}

function copyPromoCode() {
    const offer = currentOffer || likedOffers.find(o => o.id === currentOffer?.id);
    if (offer && offer.promo_code) {
        navigator.clipboard.writeText(offer.promo_code).then(() => {
            showSuccess('Promo code copied to clipboard!');
        }).catch(() => {
            showError('Failed to copy promo code');
        });
    } else {
        showError('No promo code available for this offer');
    }
}

function useOfferFromList(offerId) {
    const offer = likedOffers.find(o => o.id == offerId);
    if (offer && offer.referral_link) {
        window.open(offer.referral_link, '_blank');
    } else {
        showError('No referral link available for this offer');
    }
}

function copyPromoCodeFromList(offerId) {
    const offer = likedOffers.find(o => o.id == offerId);
    if (offer && offer.promo_code) {
        navigator.clipboard.writeText(offer.promo_code).then(() => {
            showSuccess('Promo code copied to clipboard!');
        }).catch(() => {
            showError('Failed to copy promo code');
        });
    } else {
        showError('No promo code available for this offer');
    }
}

// Test function to manually trigger liked offers
function testLikedOffers() {
    console.log('testLikedOffers() called');
    showLikedOffers();
}

// Close modals when clicking overlay
document.getElementById('modal-overlay').addEventListener('click', () => {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.add('hidden');
    });
    document.getElementById('modal-overlay').classList.add('hidden');
});

// Prevent modal close when clicking modal content
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        e.stopPropagation();
    });
});
