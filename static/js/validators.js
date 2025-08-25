// static/js/validators.js - Validation Utilities
export function showNotification(message, type = 'success', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification-popup ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => { notification.classList.add('show'); }, 100);
    
    setTimeout(() => {
        notification.classList.add('hide');
        notification.addEventListener('transitionend', () => notification.remove());
    }, duration);
}

export function showValidationError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'validation-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #f44336;
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        z-index: 10000;
        font-size: 14px;
    `;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

export function showRefreshNotification(message, type = 'success', duration = 3000) {
    const existing = document.querySelector('.refresh-notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `refresh-notification ${type}`;
    
    notification.innerHTML = `
        <span style="margin-right: 8px;">${type === 'success' ? '✅' : '❌'}</span>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Force reflow
    notification.offsetHeight;
    
    // Show animation
    requestAnimationFrame(() => {
        notification.classList.add('show');
    });
    
    // Auto hide
    setTimeout(() => {
        notification.classList.add('hide');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 400);
    }, duration);
}