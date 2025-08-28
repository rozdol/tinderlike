// Push Notification Service for Tinder-like App
class PushNotificationService {
    constructor() {
        this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
        this.registration = null;
        this.subscription = null;
        this.vapidPublicKey = null;
    }

    async initialize() {
        if (!this.isSupported) {
            console.warn('Push notifications are not supported in this browser');
            return false;
        }

        try {
            // Register service worker
            this.registration = await navigator.serviceWorker.register('/sw.js');
            console.log('Service Worker registered:', this.registration);

            // Get VAPID public key from server
            await this.getVapidPublicKey();

            // Check if user is already subscribed
            this.subscription = await this.registration.pushManager.getSubscription();
            
            if (this.subscription) {
                console.log('User is already subscribed to push notifications');
                return true;
            }

            return true;
        } catch (error) {
            console.error('Error initializing push notifications:', error);
            return false;
        }
    }

    async getVapidPublicKey() {
        try {
            const response = await fetch(`${config.API_BASE_URL}/push/vapid-public-key`);
            const data = await response.json();
            this.vapidPublicKey = data.public_key;
        } catch (error) {
            console.error('Error getting VAPID public key:', error);
        }
    }

    async requestPermission() {
        if (!this.isSupported) {
            throw new Error('Push notifications are not supported');
        }

        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
            throw new Error('Notification permission denied');
        }

        return permission;
    }

    async subscribe() {
        if (!this.isSupported || !this.vapidPublicKey) {
            throw new Error('Push notifications not supported or VAPID key not available');
        }

        try {
            // Request permission first
            await this.requestPermission();

            // Subscribe to push notifications
            this.subscription = await this.registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
            });

            // Send subscription to server
            await this.sendSubscriptionToServer(this.subscription);

            console.log('Successfully subscribed to push notifications');
            return true;
        } catch (error) {
            console.error('Error subscribing to push notifications:', error);
            throw error;
        }
    }

    async unsubscribe() {
        if (!this.subscription) {
            console.log('No active subscription to unsubscribe from');
            return true;
        }

        try {
            // Unsubscribe from push manager
            await this.subscription.unsubscribe();

            // Notify server
            await this.removeSubscriptionFromServer(this.subscription.endpoint);

            this.subscription = null;
            console.log('Successfully unsubscribed from push notifications');
            return true;
        } catch (error) {
            console.error('Error unsubscribing from push notifications:', error);
            throw error;
        }
    }

    async sendSubscriptionToServer(subscription) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('User not authenticated');
        }

        const response = await fetch(`${config.API_BASE_URL}/push/subscribe`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                endpoint: subscription.endpoint,
                keys: {
                    p256dh: this.arrayBufferToBase64(subscription.getKey('p256dh')),
                    auth: this.arrayBufferToBase64(subscription.getKey('auth'))
                }
            })
        });

        if (!response.ok) {
            throw new Error('Failed to send subscription to server');
        }

        return await response.json();
    }

    async removeSubscriptionFromServer(endpoint) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('User not authenticated');
        }

        const response = await fetch(`${config.API_BASE_URL}/push/unsubscribe?endpoint=${encodeURIComponent(endpoint)}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to remove subscription from server');
        }

        return await response.json();
    }

    async testNotification() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('User not authenticated');
        }

        const response = await fetch(`${config.API_BASE_URL}/push/test`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to send test notification');
        }

        return await response.json();
    }

    // Utility functions
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    }

    // Check if user has permission
    hasPermission() {
        return Notification.permission === 'granted';
    }

    // Check if user is subscribed
    isSubscribed() {
        return this.subscription !== null;
    }

    // Get subscription status
    getStatus() {
        return {
            supported: this.isSupported,
            permission: Notification.permission,
            subscribed: this.isSubscribed(),
            hasPermission: this.hasPermission()
        };
    }
}

// Global instance
const pushService = new PushNotificationService();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    if (pushService.isSupported) {
        await pushService.initialize();
        console.log('Push notification service initialized');
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PushNotificationService;
}

