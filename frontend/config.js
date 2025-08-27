// Configuration file for API settings
// This file can be easily updated for different environments

const config = {
    // API Base URL - automatically detects environment
    API_BASE_URL: (() => {
        const hostname = window.location.hostname;
        const port = window.location.port;
        
        // Development environment
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return `http://localhost:8000/api/v1`;
        }
        
        // Production environment - use relative URL (same domain)
        return '/api/v1';
    })(),
    
    // API endpoints
    ENDPOINTS: {
        AUTH: {
            LOGIN: '/auth/login',
            REGISTER: '/auth/register',
            VERIFY: '/auth/verify',
            REFRESH: '/auth/refresh'
        },
        OFFERS: {
            NEXT: '/offers/next',
            SWIPE: '/offers/swipe',
            LIKED: '/offers/liked'
        },
        USERS: {
            PROFILE: '/users/profile',
            NOTIFICATIONS: '/users/notifications'
        },
        ADMIN: {
            USERS: '/admin/users',
            OFFERS: '/admin/offers',
            ACTIONS: '/admin/actions',
            STATS: '/admin/stats'
        }
    },
    
    // App settings
    APP: {
        NAME: 'Tinder-like App',
        VERSION: '1.0.0',
        DEBUG: (() => {
            const hostname = window.location.hostname;
            return hostname === 'localhost' || hostname === '127.0.0.1';
        })()
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = config;
}
