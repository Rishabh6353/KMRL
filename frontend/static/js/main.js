// Main JavaScript for Intelligent Document Processing System

// Global variables
let currentTheme = 'light';
let notifications = [];

// Handle page transitions
window.addEventListener('beforeunload', function() {
    localStorage.setItem('pageIsLoading', 'true');
});

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Handle the page loader
    const pageLoader = document.getElementById('pageLoader');
    
    // Show content with a slight delay for smoother transition
    setTimeout(function() {
        if (pageLoader) {
            pageLoader.classList.add('fade-out');
        }
        
        // Remove the loader from DOM after transition
        setTimeout(function() {
            if (pageLoader) {
                pageLoader.style.display = 'none';
            }
        }, 500);
        
        // Clear the loading state
        localStorage.removeItem('pageIsLoading');
    }, 300);
    
    // Initialize the app
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize theme (already pre-initialized in head)
    initializeTheme();
    
    // Initialize notifications
    initializeNotifications();
    
    // Initialize auto-refresh for processing status
    initializeAutoRefresh();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeTheme() {
    // Check for saved theme preference, system preference, or default to light
    if (localStorage.getItem('theme')) {
        // If theme is explicitly set in localStorage, use that
        setTheme(localStorage.getItem('theme'));
    } else {
        // Check if user prefers dark mode at system level
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setTheme('dark');
        } else {
            setTheme('light');
        }
        
        // Listen for changes in system theme preference
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
            if (!localStorage.getItem('theme')) { // Only update if user hasn't manually set a theme
                setTheme(event.matches ? 'dark' : 'light');
            }
        });
    }
    
    // Mark the body as theme-initialized to enable transitions
    setTimeout(() => {
        document.body.classList.add('theme-initialized');
    }, 300);
}

function setTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update theme toggle button if it exists
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        // Add a small animation effect
        themeToggle.classList.add('rotate');
        
        setTimeout(() => {
            themeToggle.innerHTML = theme === 'dark' ? 
                '<i class="fas fa-sun"></i>' : 
                '<i class="fas fa-moon"></i>';
            
            // Remove animation class after transition completes
            setTimeout(() => {
                themeToggle.classList.remove('rotate');
            }, 300);
        }, 150);
    }
}

function toggleTheme() {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

function initializeNotifications() {
    // Check if browser supports notifications
    if ('Notification' in window) {
        // Request permission if not already granted
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
}

function showNotification(title, message, type = 'info') {
    // Browser notification
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: message,
            icon: '/static/favicon.ico'
        });
    }
    
    // In-app notification
    showAlert(message, type);
}

function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer') || createAlertContainer();
    
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" id="${alertId}" role="alert">
            <div class="d-flex align-items-center">
                <i class="fas ${getAlertIcon(type)} me-2"></i>
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-remove alert after duration
    if (duration > 0) {
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }
        }, duration);
    }
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

function getAlertIcon(type) {
    const icons = {
        'success': 'fa-check-circle',
        'danger': 'fa-exclamation-triangle',
        'warning': 'fa-exclamation-circle',
        'info': 'fa-info-circle',
        'primary': 'fa-info-circle',
        'secondary': 'fa-info-circle'
    };
    return icons[type] || 'fa-info-circle';
}

function initializeAutoRefresh() {
    // Auto-refresh processing documents every 10 seconds
    const processingElements = document.querySelectorAll('[data-status="processing"]');
    
    if (processingElements.length > 0) {
        setInterval(() => {
            refreshProcessingStatus();
        }, 10000);
    }
}

function refreshProcessingStatus() {
    const processingElements = document.querySelectorAll('[data-status="processing"]');
    
    processingElements.forEach(element => {
        const docId = element.getAttribute('data-doc-id');
        if (docId) {
            checkDocumentStatus(docId);
        }
    });
}

function checkDocumentStatus(docId) {
    fetch(`/api/document/${docId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'processing') {
                // Status has changed, refresh the page or update the element
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error checking document status:', error);
        });
}

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + U: Upload new document
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            window.location.href = '/upload';
        }
        
        // Ctrl/Cmd + D: Go to documents page
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            window.location.href = '/documents';
        }
        
        // Ctrl/Cmd + H: Go to dashboard
        if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
            e.preventDefault();
            window.location.href = '/';
        }
        
        // Escape: Close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Text copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert('Text copied to clipboard!', 'success');
    } catch (err) {
        showAlert('Failed to copy text to clipboard.', 'danger');
    }
    
    document.body.removeChild(textArea);
}

function debounce(func, wait, immediate) {
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
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// API helper functions
function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

function uploadFile(file, onProgress = null) {
    return new Promise((resolve, reject) => {
        const formData = new FormData();
        formData.append('file', file);
        
        const xhr = new XMLHttpRequest();
        
        if (onProgress) {
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    onProgress(percentComplete);
                }
            });
        }
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    resolve(response);
                } catch (e) {
                    reject(new Error('Invalid JSON response'));
                }
            } else {
                reject(new Error(`Upload failed with status: ${xhr.status}`));
            }
        });
        
        xhr.addEventListener('error', () => {
            reject(new Error('Upload failed'));
        });
        
        xhr.open('POST', '/api/upload');
        xhr.send(formData);
    });
}

// Document processing functions
function processDocument(docId, showModal = true) {
    if (showModal) {
        const modal = document.getElementById('processingModal');
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }
    
    return apiRequest(`/api/process/${docId}`, { method: 'POST' })
        .then(data => {
            if (showModal) {
                const modal = document.getElementById('processingModal');
                if (modal) {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) {
                        bsModal.hide();
                    }
                }
            }
            
            if (data.success) {
                showAlert('Document processed successfully!', 'success');
                return data;
            } else {
                throw new Error(data.error || 'Processing failed');
            }
        })
        .catch(error => {
            if (showModal) {
                const modal = document.getElementById('processingModal');
                if (modal) {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) {
                        bsModal.hide();
                    }
                }
            }
            
            showAlert(`Error processing document: ${error.message}`, 'danger');
            throw error;
        });
}

// Loading states
function showLoading(element, text = 'Loading...') {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        element.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">${text}</p>
            </div>
        `;
    }
}

function hideLoading(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        const spinner = element.querySelector('.spinner-border');
        if (spinner) {
            spinner.parentElement.remove();
        }
    }
}

// Error handling
function showError(element, message, retry = null) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        let html = `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3 opacity-90"></i>
                <h5 class="text-danger">Error</h5>
                <p>${message}</p>
        `;
        
        if (retry) {
            html += `
                <button class="btn btn-outline-primary" onclick="${retry}">
                    <i class="fas fa-sync-alt me-2"></i>
                    Try Again
                </button>
            `;
        }
        
        html += '</div>';
        element.innerHTML = html;
    }
}

// Export functions to global scope
window.IDP = {
    showAlert,
    showNotification,
    formatFileSize,
    formatDate,
    copyToClipboard,
    apiRequest,
    uploadFile,
    processDocument,
    showLoading,
    hideLoading,
    showError,
    toggleTheme
};