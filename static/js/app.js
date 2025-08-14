// static/js/app.js - Main Application Logic
import DropdownManager from './dropdown.js';
import BulkFormManager from './bulk-form.js';
import { showNotification, showValidationError } from './validators.js';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize managers
    const dropdownManager = new DropdownManager();
    const bulkFormManager = new BulkFormManager();
    
    // Global click handler to hide dropdowns
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.employee-search') && 
            !e.target.closest('.transport-search') && 
            !e.target.closest('.depot-search')) {
            dropdownManager.hideAllDropdowns();
        }
    });
    
    // HTMX event handlers
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.failed) {
            console.error("Yêu cầu HTMX thất bại:", evt.detail.xhr);
            showNotification("Yêu cầu thất bại", "error");
        }
    });
    
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        // Re-initialize dropdowns after content swap
        dropdownManager.initializeNewDropdowns(evt.detail.target);
    });
});
