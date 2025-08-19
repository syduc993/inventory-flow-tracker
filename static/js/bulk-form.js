// // static/js/bulk-form.js
// import { showValidationError } from './validators.js';

// class BulkFormManager {
//     constructor() {
//         this.rowCounter = 0;
//         this.bindGlobalMethods();
//         this.setupCommonFieldsWatcher(); // ✅ THÊM: Theo dõi thay đổi thông tin chung
//     }
    
//     bindGlobalMethods() {
//         // Bind methods to window for onclick handlers
//         window.addBillRow = this.addBillRow.bind(this);
//         window.removeBillRow = this.removeBillRow.bind(this);
//         window.validateBillId = this.validateBillId.bind(this);
//         window.submitBulkForm = this.submitBulkForm.bind(this);
//     }

//     // ✅ THÊM: Theo dõi thay đổi thông tin chung để re-validate
//     setupCommonFieldsWatcher() {
//         // Chờ DOM ready
//         document.addEventListener('DOMContentLoaded', () => {
//             const fromDepotInput = document.querySelector('input[name="from_depot"]');
//             const toDepotInput = document.querySelector('input[name="to_depot"]');
            
//             if (fromDepotInput) {
//                 fromDepotInput.addEventListener('change', () => this.revalidateAllBillIds());
//             }
//             if (toDepotInput) {
//                 toDepotInput.addEventListener('change', () => this.revalidateAllBillIds());
//             }
//         });
//     }

//     // ✅ THÊM: Re-validate tất cả Bill ID
//     async revalidateAllBillIds() {
//         const billIdInputs = document.querySelectorAll('.bill-id-input');
        
//         for (const input of billIdInputs) {
//             if (input.value.trim()) {
//                 await this.validateBillId(input);
//             }
//         }
//     }
    
//     addBillRow() {
//         const tbody = document.querySelector('#billTable tbody');
//         if (!tbody) return;
        
//         this.rowCounter++;
        
//         const row = document.createElement('tr');
//         row.id = `row-${this.rowCounter}`;
//         row.innerHTML = `
//             <td>
//                 <input type="text" 
//                     class="form-control bill-id-input" 
//                     name="bill_ids[]" 
//                     placeholder="Nhập Bill ID"
//                     onblur="validateBillId(this)">
//             </td>
//             <td>
//                 <input type="number" 
//                     class="form-control quantity-input" 
//                     name="quantities[]" 
//                     placeholder="SL bao/tải"
//                     min="1"
//                     required>
//             </td>
//             <td class="status-cell">
//                 <span class="status-pending">⏳ Chưa kiểm tra</span>
//             </td>
//             <td>
//                 <button type="button" class="btn btn-danger btn-small" onclick="removeBillRow('${row.id}')">
//                     🗑️
//                 </button>
//             </td>
//         `;
        
//         tbody.appendChild(row);
//     }
    
//     removeBillRow(rowId) {
//         const row = document.getElementById(rowId);
//         if (row) {
//             row.remove();
//         }
//     }
    
//     async validateBillId(input) {
//         const billId = input.value.trim();
//         const row = input.closest('tr');
//         const statusCell = row.querySelector('.status-cell');
        
//         if (!billId) {
//             statusCell.innerHTML = '<span class="status-pending">⏳ Chưa kiểm tra</span>';
//             return;
//         }
        
//         // ✅ THÊM: Kiểm tra bắt buộc có Kho đi và Kho đến trước khi validate
//         const fromDepot = document.querySelector('input[name="from_depot"]')?.value || '';
//         const toDepot = document.querySelector('input[name="to_depot"]')?.value || '';
        
//         if (!fromDepot || !toDepot) {
//             statusCell.innerHTML = '<span class="status-invalid">❌ Cần chọn kho trước</span>';
//             return;
//         }
        
//         statusCell.innerHTML = '<span class="status-checking">🔄 Đang kiểm tra...</span>';
        
//         try {
//             const response = await fetch('/validate-bill-id', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/x-www-form-urlencoded',
//                 },
//                 body: `bill_id=${billId}&from_depot=${fromDepot}&to_depot=${toDepot}`
//             });
            
//             const result = await response.json();
            
//             if (result.valid) {
//                 statusCell.innerHTML = '<span class="status-valid">✅ Hợp lệ</span>';
//             } else {
//                 const errorMessage = result.message.replace('ID không hợp lệ hoặc không có dữ liệu', 'ID không hợp lệ');
//                 statusCell.innerHTML = `<span class="status-invalid">❌ ${errorMessage}</span>`;
//             }
//         } catch (error) {
//             statusCell.innerHTML = '<span class="status-error">⚠️ Lỗi kiểm tra</span>';
//             console.error('Error validating bill ID:', error);
//         }
//     }
    
//     hasInvalidIds() {
//         const invalidStatuses = document.querySelectorAll('.status-invalid');
//         return invalidStatuses.length > 0;
//     }

//     // ✅ SỬA: Validate tất cả trường bắt buộc
//     validateRequiredFields() {
//         const fromDepot = document.querySelector('input[name="from_depot"]')?.value?.trim();
//         const toDepot = document.querySelector('input[name="to_depot"]')?.value?.trim();
//         const handoverPerson = document.querySelector('input[name="handover_person"]')?.value?.trim();
//         const transportProvider = document.querySelector('input[name="transport_provider"]')?.value?.trim();
        
//         // ✅ THAY ĐỔI: Tất cả đều bắt buộc
//         if (!fromDepot) {
//             return { valid: false, message: "❌ Vui lòng chọn Kho đi" };
//         }
        
//         if (!toDepot) {
//             return { valid: false, message: "❌ Vui lòng chọn Kho đến" };
//         }
        
//         if (!handoverPerson) {
//             return { valid: false, message: "❌ Vui lòng chọn Người bàn giao" };
//         }
        
//         if (!transportProvider) {
//             return { valid: false, message: "❌ Vui lòng chọn Đơn vị vận chuyển" };
//         }
        
//         return { valid: true };
//     }

//     // ✅ SỬA: Validate số lượng bắt buộc cho tất cả Bill ID
//     validateQuantityRequirement() {
//         const rows = document.querySelectorAll('#billTable tbody tr');
        
//         for (const row of rows) {
//             const billId = row.querySelector('.bill-id-input')?.value.trim();
//             const quantity = row.querySelector('.quantity-input')?.value?.trim();
            
//             // ✅ THAY ĐỔI: Bắt buộc số lượng cho tất cả Bill ID
//             if (billId && (!quantity || quantity === '0')) {
//                 return {
//                     valid: false,
//                     message: `❌ Bill ID "${billId}": Bắt buộc nhập số lượng bao/tải`
//                 };
//             }
//         }
        
//         return { valid: true };
//     }
    
//     async submitBulkForm() {
//         const submitBtn = document.getElementById('submitBtn');
//         const resultContainer = document.getElementById('bulk-result-container');
        
//         // Validation 1: Không cho submit nếu có ID không hợp lệ
//         if (this.hasInvalidIds()) {
//             resultContainer.innerHTML = '<div class="error">❌ Vui lòng sửa các ID không hợp lệ trước khi lưu</div>';
//             return;
//         }
        
//         // ✅ SỬA: Validation 2 - Tất cả thông tin chung bắt buộc
//         const requiredValidation = this.validateRequiredFields();
//         if (!requiredValidation.valid) {
//             resultContainer.innerHTML = `<div class="error">${requiredValidation.message}</div>`;
//             return;
//         }
        
//         // ✅ SỬA: Validation 3 - Số lượng bắt buộc cho tất cả
//         const quantityValidation = this.validateQuantityRequirement();
//         if (!quantityValidation.valid) {
//             resultContainer.innerHTML = `<div class="error">${quantityValidation.message}</div>`;
//             return;
//         }
        
//         // Get fields (đã validate ở trên)
//         const fromDepot = document.querySelector('input[name="from_depot"]').value;
//         const toDepot = document.querySelector('input[name="to_depot"]').value;
//         const handoverPerson = document.querySelector('input[name="handover_person"]').value;
//         const transportProvider = document.querySelector('input[name="transport_provider"]').value;
        
//         // Get bill data
//         const rows = document.querySelectorAll('#billTable tbody tr');
//         const billData = [];
        
//         for (const row of rows) {
//             const billId = row.querySelector('.bill-id-input')?.value.trim();
//             const quantity = row.querySelector('.quantity-input')?.value;
            
//             if (billId) {
//                 billData.push({
//                     bill_id: billId,
//                     quantity: quantity || 0
//                 });
//             }
//         }
        
//         if (billData.length === 0) {
//             resultContainer.innerHTML = '<div class="error">❌ Vui lòng nhập ít nhất 1 Bill ID</div>';
//             return;
//         }
        
//         // Show loading
//         submitBtn?.classList.add('htmx-request');
//         resultContainer.innerHTML = '<div class="info">🔄 Đang xử lý...</div>';
        
//         try {
//             const response = await fetch('/bulk-create-records', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({
//                     from_depot: fromDepot,
//                     to_depot: toDepot,
//                     handover_person: handoverPerson,
//                     transport_provider: transportProvider,
//                     bill_data: billData
//                 })
//             });
            
//             const result = await response.text();
//             resultContainer.innerHTML = result;
            
//             // Reset form if successful
//             if (result.includes('success')) {
//                 const tbody = document.querySelector('#billTable tbody');
//                 if (tbody) {
//                     tbody.innerHTML = '';
//                     this.addBillRow();
//                 }
//             }
            
//         } catch (error) {
//             resultContainer.innerHTML = '<div class="error">❌ Lỗi hệ thống: ' + error.message + '</div>';
//         } finally {
//             submitBtn?.classList.remove('htmx-request');
//         }
//     }
// }

// export default BulkFormManager;



// static/js/bulk-form.js
import { showValidationError } from './validators.js';

class BulkFormManager {
    constructor() {
        this.rowCounter = 0;
        this.bindGlobalMethods();
        this.setupCommonFieldsWatcher(); // ✅ THÊM: Theo dõi thay đổi thông tin chung
    }
    
    bindGlobalMethods() {
        // Bind methods to window for onclick handlers
        window.addBillRow = this.addBillRow.bind(this);
        window.removeBillRow = this.removeBillRow.bind(this);
        window.validateBillId = this.validateBillId.bind(this);
        window.submitBulkForm = this.submitBulkForm.bind(this);
    }

    // ✅ SỬA: Theo dõi thay đổi thông tin chung để re-validate
    setupCommonFieldsWatcher() {
        // Sử dụng MutationObserver để theo dõi thay đổi giá trị
        const observeValueChanges = () => {
            const fromDepotInput = document.querySelector('input[name="from_depot"]');
            const toDepotInput = document.querySelector('input[name="to_depot"]');
            
            if (fromDepotInput && !fromDepotInput.dataset.observerAttached) {
                // Theo dõi thay đổi giá trị trực tiếp
                const observer = new MutationObserver(() => {
                    this.debounceRevalidate();
                });
                
                observer.observe(fromDepotInput, {
                    attributes: true,
                    attributeFilter: ['value']
                });
                
                // Cũng lắng nghe các events thông thường
                ['input', 'change', 'blur'].forEach(eventType => {
                    fromDepotInput.addEventListener(eventType, () => this.debounceRevalidate());
                });
                
                fromDepotInput.dataset.observerAttached = 'true';
            }
            
            if (toDepotInput && !toDepotInput.dataset.observerAttached) {
                // Theo dõi thay đổi giá trị trực tiếp
                const observer = new MutationObserver(() => {
                    this.debounceRevalidate();
                });
                
                observer.observe(toDepotInput, {
                    attributes: true,
                    attributeFilter: ['value']
                });
                
                // Cũng lắng nghe các events thông thường
                ['input', 'change', 'blur'].forEach(eventType => {
                    toDepotInput.addEventListener(eventType, () => this.debounceRevalidate());
                });
                
                toDepotInput.dataset.observerAttached = 'true';
            }
        };
        
        // Thực hiện ngay lập tức
        observeValueChanges();
        
        // Theo dõi DOM changes để catch khi dropdown được khởi tạo
        const domObserver = new MutationObserver(observeValueChanges);
        domObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Cũng setup khi DOMContentLoaded
        document.addEventListener('DOMContentLoaded', observeValueChanges);
        
        // Polling fallback để đảm bảo chắc chắn
        setInterval(() => {
            this.checkForValueChanges();
        }, 1000);
    }

    // ✅ THÊM: Polling fallback để check thay đổi giá trị
    checkForValueChanges() {
        const fromDepotInput = document.querySelector('input[name="from_depot"]');
        const toDepotInput = document.querySelector('input[name="to_depot"]');
        
        if (fromDepotInput) {
            const currentValue = fromDepotInput.value;
            if (currentValue !== this.lastFromDepotValue) {
                this.lastFromDepotValue = currentValue;
                this.debounceRevalidate();
            }
        }
        
        if (toDepotInput) {
            const currentValue = toDepotInput.value;
            if (currentValue !== this.lastToDepotValue) {
                this.lastToDepotValue = currentValue;
                this.debounceRevalidate();
            }
        }
    }

    // ✅ THÊM: Debounce để tránh spam revalidation
    debounceRevalidate() {
        clearTimeout(this.revalidateTimeout);
        this.revalidateTimeout = setTimeout(() => {
            console.log('🔄 Revalidating all Bill IDs due to depot changes...');
            this.revalidateAllBillIds();
        }, 500); // Đợi 500ms sau thay đổi cuối
    }

    // ✅ SỬA: Re-validate tất cả Bill ID với logging
    async revalidateAllBillIds() {
        const billIdInputs = document.querySelectorAll('.bill-id-input');
        console.log(`🔍 Found ${billIdInputs.length} Bill ID inputs to revalidate`);
        
        for (const input of billIdInputs) {
            if (input.value.trim()) {
                console.log(`🔄 Revalidating Bill ID: ${input.value}`);
                await this.validateBillId(input);
            }
        }
        
        console.log('✅ Revalidation completed');
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
                    min="1"
                    required>
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
        
        // ✅ THÊM: Kiểm tra bắt buộc có Kho đi và Kho đến trước khi validate
        const fromDepot = document.querySelector('input[name="from_depot"]')?.value || '';
        const toDepot = document.querySelector('input[name="to_depot"]')?.value || '';
        
        if (!fromDepot || !toDepot) {
            statusCell.innerHTML = '<span class="status-invalid">❌ Cần chọn kho trước</span>';
            return;
        }
        
        statusCell.innerHTML = '<span class="status-checking">🔄 Đang kiểm tra...</span>';
        
        try {
            const response = await fetch('/validate-bill-id', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `bill_id=${billId}&from_depot=${fromDepot}&to_depot=${toDepot}`
            });
            
            const result = await response.json();
            
            if (result.valid) {
                statusCell.innerHTML = '<span class="status-valid">✅ Hợp lệ</span>';
            } else {
                const errorMessage = result.message.replace('ID không hợp lệ hoặc không có dữ liệu', 'ID không hợp lệ');
                statusCell.innerHTML = `<span class="status-invalid">❌ ${errorMessage}</span>`;
            }
        } catch (error) {
            statusCell.innerHTML = '<span class="status-error">⚠️ Lỗi kiểm tra</span>';
            console.error('Error validating bill ID:', error);
        }
    }
    
    hasInvalidIds() {
        const invalidStatuses = document.querySelectorAll('.status-invalid');
        return invalidStatuses.length > 0;
    }

    // ✅ SỬA: Validate tất cả trường bắt buộc
    validateRequiredFields() {
        const fromDepot = document.querySelector('input[name="from_depot"]')?.value?.trim();
        const toDepot = document.querySelector('input[name="to_depot"]')?.value?.trim();
        const handoverPerson = document.querySelector('input[name="handover_person"]')?.value?.trim();
        const transportProvider = document.querySelector('input[name="transport_provider"]')?.value?.trim();
        
        // ✅ THAY ĐỔI: Tất cả đều bắt buộc
        if (!fromDepot) {
            return { valid: false, message: "❌ Vui lòng chọn Kho đi" };
        }
        
        if (!toDepot) {
            return { valid: false, message: "❌ Vui lòng chọn Kho đến" };
        }
        
        if (!handoverPerson) {
            return { valid: false, message: "❌ Vui lòng chọn Người bàn giao" };
        }
        
        if (!transportProvider) {
            return { valid: false, message: "❌ Vui lòng chọn Đơn vị vận chuyển" };
        }
        
        return { valid: true };
    }

    // ✅ SỬA: Validate số lượng bắt buộc cho tất cả Bill ID
    validateQuantityRequirement() {
        const rows = document.querySelectorAll('#billTable tbody tr');
        
        for (const row of rows) {
            const billId = row.querySelector('.bill-id-input')?.value.trim();
            const quantity = row.querySelector('.quantity-input')?.value?.trim();
            
            // ✅ THAY ĐỔI: Bắt buộc số lượng cho tất cả Bill ID
            if (billId && (!quantity || quantity === '0')) {
                return {
                    valid: false,
                    message: `❌ Bill ID "${billId}": Bắt buộc nhập số lượng bao/tải`
                };
            }
        }
        
        return { valid: true };
    }
    
    async submitBulkForm() {
        const submitBtn = document.getElementById('submitBtn');
        const resultContainer = document.getElementById('bulk-result-container');
        
        // Validation 1: Không cho submit nếu có ID không hợp lệ
        if (this.hasInvalidIds()) {
            resultContainer.innerHTML = '<div class="error">❌ Vui lòng sửa các ID không hợp lệ trước khi lưu</div>';
            return;
        }
        
        // ✅ SỬA: Validation 2 - Tất cả thông tin chung bắt buộc
        const requiredValidation = this.validateRequiredFields();
        if (!requiredValidation.valid) {
            resultContainer.innerHTML = `<div class="error">${requiredValidation.message}</div>`;
            return;
        }
        
        // ✅ SỬA: Validation 3 - Số lượng bắt buộc cho tất cả
        const quantityValidation = this.validateQuantityRequirement();
        if (!quantityValidation.valid) {
            resultContainer.innerHTML = `<div class="error">${quantityValidation.message}</div>`;
            return;
        }
        
        // Get fields (đã validate ở trên)
        const fromDepot = document.querySelector('input[name="from_depot"]').value;
        const toDepot = document.querySelector('input[name="to_depot"]').value;
        const handoverPerson = document.querySelector('input[name="handover_person"]').value;
        const transportProvider = document.querySelector('input[name="transport_provider"]').value;
        
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
