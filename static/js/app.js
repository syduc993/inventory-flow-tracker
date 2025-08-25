// static/js/app.js - Main Application Logic
import DropdownManager from './dropdown.js';
import BulkFormManager from './bulk-form.js';
import { showNotification, showValidationError, showRefreshNotification } from './validators.js';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize managers
    const dropdownManager = new DropdownManager();
    const bulkFormManager = new BulkFormManager();
    
    // ✅ SỬA: Gán hàm vào window để <script> trong HTML có thể gọi
    window.showRefreshNotification = showRefreshNotification;
    
    // Global click handler to hide dropdowns
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.employee-search') && 
            !e.target.closest('.transport-search') && 
            !e.target.closest('.depot-search')) {
            dropdownManager.hideAllDropdowns();
        }
    });
    
    // HTMX event handlers (giữ lại để xử lý lỗi chung)
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.failed) {
            console.error("Yêu cầu HTMX thất bại:", evt.detail.xhr);
            showNotification("Yêu cầu thất bại", "error");
        }
    });
    
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        // Re-initialize dropdowns after content swap
        // dropdownManager.initializeNewDropdowns(evt.detail.target);
        dropdownManager.initializeAll();
    });
});
