import { showValidationError } from './validators.js';

class BulkFormManager {
    constructor() {
        this.rowCounter = 0;
        this.bindGlobalMethods();
    }
    
    bindGlobalMethods() {
        // Bind methods to window for onclick handlers
        window.addBillRow = this.addBillRow.bind(this);
        window.removeBillRow = this.removeBillRow.bind(this);
        window.validateBillId = this.validateBillId.bind(this);
        // ✅ BỎ: validateAllIds - không cần kiểm tra tất cả nữa
        window.submitBulkForm = this.submitBulkForm.bind(this);
    }
    
    addBillRow() {
        const tbody = document.querySelector('#billTable tbody');
        if (!tbody) return;
        
        this.rowCounter++;
        
        const row = document.createElement('tr');
        row.id = `row-${this.rowCounter}`;
        row.innerHTML = `
            <td>
                <input type="text" 
                    class="form-control bill-id-input" 
                    name="bill_ids[]" 
                    placeholder="Nhập Bill ID"
                    onblur="validateBillId(this)">
            </td>
            <td>
                <input type="number" 
                    class="form-control quantity-input" 
                    name="quantities[]" 
                    placeholder="SL bao/tải"
                    min="1">
            </td>
            <td class="status-cell">
                <span class="status-pending">⏳ Chưa kiểm tra</span>
            </td>
            <td>
                <button type="button" class="btn btn-danger btn-small" onclick="removeBillRow('${row.id}')">
                    🗑️
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    }
    
    removeBillRow(rowId) {
        const row = document.getElementById(rowId);
        if (row) {
            row.remove();
        }
    }
    
    async validateBillId(input) {
        const billId = input.value.trim();
        const row = input.closest('tr');
        const statusCell = row.querySelector('.status-cell');
        
        if (!billId) {
            statusCell.innerHTML = '<span class="status-pending">⏳ Chưa kiểm tra</span>';
            return;
        }
        
        statusCell.innerHTML = '<span class="status-checking">🔄 Đang kiểm tra...</span>';
        
        try {
            const response = await fetch('/validate-bill-id', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `bill_id=${billId}`
            });
            
            const result = await response.json();
            
            if (result.valid) {
                statusCell.innerHTML = '<span class="status-valid">✅ Hợp lệ</span>';
                const quantityInput = row.querySelector('.quantity-input');
                if (result.quantity && !quantityInput.value) {
                    quantityInput.value = result.quantity;
                }
            } else {
                // ✅ SỬA: Rút gọn thông báo lỗi từ "ID không hợp lệ hoặc không có dữ liệu" thành "ID không hợp lệ"
                const errorMessage = result.message.replace('ID không hợp lệ hoặc không có dữ liệu', 'ID không hợp lệ');
                statusCell.innerHTML = `<span class="status-invalid">❌ ${errorMessage}</span>`;
            }
        } catch (error) {
            statusCell.innerHTML = '<span class="status-error">⚠️ Lỗi kiểm tra</span>';
            console.error('Error validating bill ID:', error);
        }
    }
    
    // ✅ BỎ: validateAllIds method - không cần nữa vì mỗi ID đã tự kiểm tra
    
    // ✅ THÊM: Helper method để kiểm tra có ID không hợp lệ không
    hasInvalidIds() {
        const invalidStatuses = document.querySelectorAll('.status-invalid');
        return invalidStatuses.length > 0;
    }
    
    async submitBulkForm() {
        const submitBtn = document.getElementById('submitBtn');
        const resultContainer = document.getElementById('bulk-result-container');
        
        // ✅ SỬA: Validation frontend - không cho submit nếu có ID không hợp lệ
        if (this.hasInvalidIds()) {
            resultContainer.innerHTML = '<div class="error">❌ Vui lòng sửa các ID không hợp lệ trước khi lưu</div>';
            return;
        }
        
        // Get common fields
        const fromDepot = document.querySelector('input[name="from_depot"]')?.value;
        const toDepot = document.querySelector('input[name="to_depot"]')?.value;
        const handoverPerson = document.querySelector('input[name="handover_person"]')?.value;
        const transportProvider = document.querySelector('input[name="transport_provider"]')?.value || '';
        
        // Validate common fields
        if (!fromDepot || !toDepot || !handoverPerson) {
            resultContainer.innerHTML = '<div class="error">❌ Vui lòng điền đầy đủ thông tin bắt buộc (Kho đi, Kho đến, Người bàn giao)</div>';
            return;
        }
        
        // Get bill data
        const rows = document.querySelectorAll('#billTable tbody tr');
        const billData = [];
        
        for (const row of rows) {
            const billId = row.querySelector('.bill-id-input')?.value.trim();
            const quantity = row.querySelector('.quantity-input')?.value;
            
            if (billId) {
                billData.push({
                    bill_id: billId,
                    quantity: quantity || 0
                });
            }
        }
        
        if (billData.length === 0) {
            resultContainer.innerHTML = '<div class="error">❌ Vui lòng nhập ít nhất 1 Bill ID</div>';
            return;
        }
        
        // Show loading
        submitBtn?.classList.add('htmx-request');
        resultContainer.innerHTML = '<div class="info">🔄 Đang xử lý...</div>';
        
        try {
            const response = await fetch('/bulk-create-records', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    from_depot: fromDepot,
                    to_depot: toDepot,
                    handover_person: handoverPerson,
                    transport_provider: transportProvider,
                    bill_data: billData
                })
            });
            
            const result = await response.text();
            resultContainer.innerHTML = result;
            
            // Reset form if successful
            if (result.includes('success')) {
                const tbody = document.querySelector('#billTable tbody');
                if (tbody) {
                    tbody.innerHTML = '';
                    this.addBillRow();
                }
            }
            
        } catch (error) {
            resultContainer.innerHTML = '<div class="error">❌ Lỗi hệ thống: ' + error.message + '</div>';
        } finally {
            submitBtn?.classList.remove('htmx-request');
        }
    }
}

export default BulkFormManager;
