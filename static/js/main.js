// Saski AI WooCommerce Integration - Main JavaScript

// Global utilities
window.SaskiWooCommerce = {
    // Show loading overlay
    showLoading: function(text = 'Processing...') {
        const overlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        
        if (loadingText) {
            loadingText.textContent = text;
        }
        
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    },
    
    // Hide loading overlay
    hideLoading: function() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    },
    
    // Show toast notification
    showToast: function(type, message, duration = 5000) {
        const toast = document.getElementById('toast');
        const toastIcon = document.getElementById('toastIcon');
        const toastMessage = document.getElementById('toastMessage');
        
        if (!toast || !toastIcon || !toastMessage) return;
        
        // Set icon based on type
        let iconClass = 'mdi-information';
        switch (type) {
            case 'success':
                iconClass = 'mdi-check-circle';
                break;
            case 'error':
                iconClass = 'mdi-alert-circle';
                break;
            case 'warning':
                iconClass = 'mdi-alert';
                break;
            case 'info':
                iconClass = 'mdi-information';
                break;
        }
        
        // Update content
        toastIcon.className = `mdi ${iconClass}`;
        toastMessage.textContent = message;
        
        // Update toast class
        toast.className = `toast ${type}`;
        
        // Show toast
        toast.classList.remove('hidden');
        
        // Auto-hide after duration
        setTimeout(() => {
            toast.classList.add('hidden');
        }, duration);
    },
    
    // Format date/time
    formatDateTime: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    },
    
    // Format relative time
    formatRelativeTime: function(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        
        return date.toLocaleDateString();
    },
    
    // Validate URL
    isValidUrl: function(string) {
        try {
            const url = new URL(string.startsWith('http') ? string : 'https://' + string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch (_) {
            return false;
        }
    },
    
    // Debounce function
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },
    
    // API request helper
    apiRequest: async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
};

// Expose utilities globally for template use
window.showLoading = window.SaskiWooCommerce.showLoading;
window.hideLoading = window.SaskiWooCommerce.hideLoading;
window.showToast = window.SaskiWooCommerce.showToast;

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });
    
    // Initialize tooltips if any
    initializeTooltips();
    
    // Initialize auto-refresh for dashboard
    if (window.location.pathname === '/') {
        initializeDashboardRefresh();
    }
});

// Initialize tooltips
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const text = event.target.getAttribute('data-tooltip');
    if (!text) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: #374151;
        color: white;
        padding: 0.5rem 0.75rem;
        border-radius: 0.375rem;
        font-size: 0.75rem;
        z-index: 1000;
        pointer-events: none;
        white-space: nowrap;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.bottom + 5 + 'px';
    
    event.target._tooltip = tooltip;
}

function hideTooltip(event) {
    if (event.target._tooltip) {
        document.body.removeChild(event.target._tooltip);
        event.target._tooltip = null;
    }
}

// Dashboard auto-refresh
function initializeDashboardRefresh() {
    const refreshInterval = 30000; // 30 seconds
    
    setInterval(async () => {
        try {
            const stats = await window.SaskiWooCommerce.apiRequest('/api/stats');
            updateDashboardStats(stats);
        } catch (error) {
            console.log('Dashboard refresh failed:', error);
        }
    }, refreshInterval);
}

function updateDashboardStats(stats) {
    const statNumbers = document.querySelectorAll('.stat-number');
    if (statNumbers.length >= 3) {
        statNumbers[0].textContent = stats.total_stores || 0;
        statNumbers[1].textContent = stats.active_stores || 0;
        statNumbers[2].textContent = stats.recent_connections || 0;
    }
}

// Form validation helpers
window.FormValidator = {
    validateStoreUrl: function(url) {
        if (!url) return { valid: false, message: 'Store URL is required' };
        
        // Add protocol if missing
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            url = 'https://' + url;
        }
        
        if (!window.SaskiWooCommerce.isValidUrl(url)) {
            return { valid: false, message: 'Please enter a valid URL' };
        }
        
        return { valid: true, url: url };
    },
    
    validateUsername: function(username) {
        if (!username || username.trim().length === 0) {
            return { valid: false, message: 'Username is required' };
        }
        
        if (username.trim().length < 3) {
            return { valid: false, message: 'Username must be at least 3 characters' };
        }
        
        return { valid: true };
    },
    
    validatePassword: function(password) {
        if (!password || password.length === 0) {
            return { valid: false, message: 'Password is required' };
        }
        
        if (password.length < 6) {
            return { valid: false, message: 'Password must be at least 6 characters' };
        }
        
        return { valid: true };
    },
    
    showFieldError: function(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        // Remove existing error
        this.clearFieldError(fieldId);
        
        // Add error styling
        field.classList.add('error');
        field.style.borderColor = 'var(--error)';
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.cssText = `
            color: var(--error);
            font-size: 0.75rem;
            margin-top: 0.25rem;
        `;
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    },
    
    clearFieldError: function(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        field.classList.remove('error');
        field.style.borderColor = '';
        
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    },
    
    clearAllErrors: function() {
        const errorFields = document.querySelectorAll('.error');
        errorFields.forEach(field => {
            field.classList.remove('error');
            field.style.borderColor = '';
        });
        
        const errorMessages = document.querySelectorAll('.field-error');
        errorMessages.forEach(error => error.remove());
    }
};

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Escape key to close modals
    if (event.key === 'Escape') {
        const visibleModals = document.querySelectorAll('.modal:not(.hidden)');
        visibleModals.forEach(modal => {
            modal.classList.add('hidden');
        });
    }
    
    // Ctrl+/ for help (future implementation)
    if (event.ctrlKey && event.key === '/') {
        event.preventDefault();
        // Show help modal or navigate to docs
        console.log('Help shortcut triggered');
    }
});

// Close modals when clicking outside
document.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal:not(.hidden)');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.classList.add('hidden');
        }
    });
});

// Handle connection/network errors
window.addEventListener('online', function() {
    window.SaskiWooCommerce.showToast('success', 'Connection restored');
});

window.addEventListener('offline', function() {
    window.SaskiWooCommerce.showToast('warning', 'Connection lost. Some features may not work.');
});

// Console welcome message
console.log('%c🚀 Saski AI WooCommerce Integration', 'color: #5243E9; font-size: 16px; font-weight: bold;');
console.log('%cBuilt with ❤️ for seamless WooCommerce integration', 'color: #64748B; font-size: 12px;');

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.SaskiWooCommerce;
} 