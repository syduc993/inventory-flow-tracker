// // static/js/bulk-form.js
// import { showValidationError } from './validators.js';

// class BulkFormManager {
//     constructor() {
//         this.rowCounter = 0;
//         this.groupCounter = 0;
//         this.lastFromDepotValue = '';
//         this.lastToDepotValue = '';
//         this.revalidateTimeout = null;

//         this.bindGlobalMethods();
//         this.setupCommonFieldsWatcher();
//     }
    
//     bindGlobalMethods() {
//         // Gắn các phương thức vào window để HTML có thể gọi qua onclick
//         window.addSingleBillRow = this.addSingleBillRow.bind(this);
//         window.showGroupedBillModal = this.showGroupedBillModal.bind(this);
//         window.closeGroupedBillModal = this.closeGroupedBillModal.bind(this);
//         window.addGroupedBillRows = this.addGroupedBillRows.bind(this);
//         window.removeBillRow = this.removeBillRow.bind(this);
//         window.removeGroupedRows = this.removeGroupedRows.bind(this);
//         window.validateBillId = this.validateBillId.bind(this);
//         window.submitBulkForm = this.submitBulkForm.bind(this);
//         window.updateTotalSummary = this.updateTotalSummary.bind(this);

//         // Các phương thức của Modal
//         window.addModalBillRow = this.addModalBillRow.bind(this);
//         window.removeModalBillRow = this.removeModalBillRow.bind(this);
//         window.validateModalBillId = this.validateModalBillId.bind(this);
//     }

//     // ✅ SỬA: Sử dụng class selector thay vì name attribute
//     setupCommonFieldsWatcher() {
//         // Lấy giá trị ban đầu
//         const depotInputs = document.querySelectorAll('.depot-hidden-input');
//         const fromDepotInput = depotInputs[0];
//         const toDepotInput = depotInputs[1];
//         this.lastFromDepotValue = fromDepotInput ? fromDepotInput.value : '';
//         this.lastToDepotValue = toDepotInput ? toDepotInput.value : '';

//         // Do component dropdown không bắn ra sự kiện 'change' tiêu chuẩn,
//         // chúng ta phải dùng polling để kiểm tra sự thay đổi giá trị.
//         // Đây là cách đáng tin cậy để trigger re-validation khi kho được chọn.
//         setInterval(() => this.checkForValueChanges(), 800);
//     }

//     checkForValueChanges() {
//         const depotInputs = document.querySelectorAll('.depot-hidden-input');
//         const fromDepotInput = depotInputs[0];
//         const toDepotInput = depotInputs[1];

//         if (fromDepotInput && fromDepotInput.value !== this.lastFromDepotValue) {
//             this.lastFromDepotValue = fromDepotInput.value;
//             this.debounceRevalidate();
//         }
//         if (toDepotInput && toDepotInput.value !== this.lastToDepotValue) {
//             this.lastToDepotValue = toDepotInput.value;
//             this.debounceRevalidate();
//         }
//     }

//     debounceRevalidate() {
//         clearTimeout(this.revalidateTimeout);
//         this.revalidateTimeout = setTimeout(() => this.revalidateAllBillIds(), 500);
//     }

//     async revalidateAllBillIds() {
//         const billIdInputs = document.querySelectorAll('.bill-id-input');
//         for (const input of billIdInputs) {
//             if (input.value.trim()) {
//                 await this.validateBillId(input);
//             }
//         }
//     }

    
//     addSingleBillRow() {
//         const tbody = document.querySelector('#billTable tbody');
//         if (!tbody) return;
//         this.rowCounter++;
//         const row = document.createElement('tr');
//         row.id = `row-${this.rowCounter}`;
//         row.classList.add('single-row');
//         row.innerHTML = `
//             <td><input type="text" class="form-control bill-id-input" placeholder="ID" onblur="validateBillId(this)"></td>
//             <td><input type="number" class="form-control bag-quantity-input" placeholder="SL bao" min="0"></td>
//             <td><input type="number" class="form-control quantity-input" placeholder="SL tải" min="1" required oninput="updateTotalSummary()"></td>
//             <td class="status-cell"><span class="status-pending">⏳ Chưa kiểm tra</span></td>
//             <td class="action-cell"><button type="button" class="btn btn-danger btn-small" onclick="removeBillRow('${row.id}')">🗑️</button></td>
//         `;
//         tbody.appendChild(row);
//         this.updateTotalSummary();
//     }



//     addModalBillRow() {
//         const modalTbody = document.getElementById('modalBillTbody');
//         if (!modalTbody) return;
        
//         const newRow = modalTbody.insertRow();
//         newRow.innerHTML = `
//             <td><input type="text" class="form-control modal-bill-id-input" placeholder="ID" onblur="validateModalBillId(this)"></td>
//             <td class="status-cell"><span class="status-pending">⏳ Chưa kiểm tra</span></td>
//             <td class="action-cell"><button type="button" class="btn btn-danger btn-small" onclick="removeModalBillRow(this)">🗑️</button></td>
//         `;
//         const newInput = newRow.querySelector('input');
//         if (newInput) {
//             newInput.focus();
//         }
//     }

//     removeModalBillRow(button) {
//         const row = button.closest('tr');
//         if (row) {
//             row.remove();
//         }
//     }

//     async validateModalBillId(input) {
//         const billId = input.value.trim();
//         const row = input.closest('tr');
//         const statusCell = row.querySelector('.status-cell');
        
//         if (!billId) {
//             statusCell.innerHTML = '<span class="status-pending">⏳ Chưa kiểm tra</span>';
//             return;
//         }

//         // ✅ SỬA: Sử dụng class selector thay vì name attribute
//         const depotInputs = document.querySelectorAll('.depot-hidden-input');
//         const fromDepot = depotInputs[0]?.value || '';
//         const toDepot = depotInputs[1]?.value || '';
        
//         if (!fromDepot || !toDepot) {
//             statusCell.innerHTML = '<span class="status-invalid" title="Vui lòng chọn Kho đi và Kho đến ở form chính trước.">❌ Chọn kho trước</span>';
//             return;
//         }

//         statusCell.innerHTML = '<span class="status-checking">🔄 Đang KT...</span>';
        
//         try {
//             const response = await fetch('/validate-bill-id', {
//                 method: 'POST',
//                 headers: {'Content-Type': 'application/x-www-form-urlencoded'},
//                 body: `bill_id=${billId}&from_depot=${fromDepot}&to_depot=${toDepot}`
//             });
//             const result = await response.json();
            
//             if (result.valid) {
//                 statusCell.innerHTML = '<span class="status-valid">✅ Hợp lệ</span>';
//             } else {
//                 statusCell.innerHTML = `<span class="status-invalid" title="${result.message}">❌ ${result.message}</span>`;
//             }
//         } catch (error) {
//             statusCell.innerHTML = '<span class="status-error" title="Lỗi kết nối máy chủ.">⚠️ Lỗi</span>';
//         }
//     }

//     showGroupedBillModal() {
//         const modal = document.getElementById('groupedBillModal');
//         const modalTbody = document.getElementById('modalBillTbody');
        
//         if (!modal) return;

//         if (modalTbody) {
//             modalTbody.innerHTML = ''; 
//             this.addModalBillRow();
//             this.addModalBillRow();
//         }

//         modal.classList.add('show');
        
//         setTimeout(() => {
//             const firstInput = modalTbody?.querySelector('input');
//             if (firstInput) firstInput.focus();
//         }, 100);
//     }

//     closeGroupedBillModal() {
//         const modal = document.getElementById('groupedBillModal');
//         if (modal) modal.classList.remove('show');
//     }

//     addGroupedBillRows() {
//         const modalInputs = document.querySelectorAll('#modalBillTbody .modal-bill-id-input');
//         const billIds = Array.from(modalInputs).map(input => input.value.trim()).filter(id => id);

//         if (billIds.length < 2) {
//             alert('Vui lòng nhập ít nhất 2 Bill ID để gộp thành một tải.');
//             return;
//         }

//         const invalidBill = Array.from(modalInputs).find(input => {
//             const row = input.closest('tr');
//             return row && row.querySelector('.status-invalid');
//         });
        
//         if (invalidBill) {
//             alert('Tồn tại Bill ID không hợp lệ trong danh sách. Vui lòng kiểm tra lại.');
//             return;
//         }
        
//         const tbody = document.querySelector('#billTable tbody');
//         if (!tbody) return;

//         this.groupCounter++;
//         const groupId = `group-${this.groupCounter}`;
//         const groupQuantity = 1;

//         billIds.forEach((billId, index) => {
//             this.rowCounter++;
//             const row = document.createElement('tr');
//             row.id = `row-${this.rowCounter}`;
//             row.classList.add('grouped-row');
//             row.dataset.groupId = groupId;
            
//             let rowHtml = `<td><input type="text" class="form-control bill-id-input" value="${billId}" onblur="validateBillId(this)" readonly></td>`;
            
//             // ✅ THÊM: Cột SL bao - mỗi row có input riêng
//             rowHtml += `<td><input type="number" class="form-control bag-quantity-input" placeholder="SL bao" min="0"></td>`;
            
//             if (index === 0) {
//                 rowHtml += `
//                     <td rowspan="${billIds.length}" class="grouped-quantity-cell">
//                         <input type="number" class="form-control quantity-input" value="${groupQuantity}" min="1" required oninput="updateTotalSummary()">
//                         <small class="text-muted">${billIds.length} ID</small>
//                     </td>
//                 `;
//             }
            
//             rowHtml += `<td class="status-cell"><span class="status-valid">✅ Hợp lệ</span></td>`;
            
//             if (index === 0) {
//                 rowHtml += `<td rowspan="${billIds.length}" class="action-cell"><button type="button" class="btn btn-danger btn-small" onclick="removeGroupedRows('${groupId}')" title="Xóa nhóm">🗑️</button></td>`;
//             }
            
//             row.innerHTML = rowHtml;
//             tbody.appendChild(row);
//         });

//         this.closeGroupedBillModal();
//         this.updateTotalSummary();
//     }



//     removeBillRow(rowId) {
//         const row = document.getElementById(rowId);
//         if (row) {
//             row.remove();
//             this.updateTotalSummary();
//         }
//     }

//     removeGroupedRows(groupId) {
//         document.querySelectorAll(`tr[data-group-id="${groupId}"]`).forEach(row => row.remove());
//         this.updateTotalSummary();
//     }

//     async validateBillId(input) {
//         // Re-validation logic is similar to modal, just on the main table
//         await this.validateModalBillId(input);
//     }

//     updateTotalSummary() {
//         let totalBills = 0;
//         let totalLoads = 0;
        
//         document.querySelectorAll('#billTable tbody tr').forEach(row => {
//             if (row.querySelector('.bill-id-input')?.value.trim()) {
//                 totalBills++;
//             }
//             if (row.querySelector('.quantity-input')) {
//                 const quantity = parseInt(row.querySelector('.quantity-input').value, 10) || 0;
//                 totalLoads += quantity;
//             }
//         });
        
//         const totalBillsSpan = document.getElementById('totalBills');
//         const totalLoadsSpan = document.getElementById('totalLoads');
//         if(totalBillsSpan) totalBillsSpan.textContent = totalBills;
//         if(totalLoadsSpan) totalLoadsSpan.textContent = totalLoads;
//     }

//     hasInvalidIds() {
//         return document.querySelectorAll('#billTable .status-invalid').length > 0;
//     }

//     validateRequiredFields() {
//         // ✅ SỬA: Sử dụng class selector thay vì name attribute
//         const depotInputs = document.querySelectorAll('.depot-hidden-input');
//         const fromDepot = depotInputs[0]?.value || '';
//         const toDepot = depotInputs[1]?.value || '';
        
//         const handoverPersonInput = document.querySelector('.employee-hidden-input');
//         const transportProviderInput = document.querySelector('.transport-hidden-input');
        
//         if (!fromDepot) {
//             return { valid: false, message: `❌ Vui lòng chọn Kho đi.` };
//         }
//         if (!toDepot) {
//             return { valid: false, message: `❌ Vui lòng chọn Kho đến.` };
//         }
//         if (!handoverPersonInput?.value) {
//             return { valid: false, message: `❌ Vui lòng chọn Người bàn giao.` };
//         }
//         if (!transportProviderInput?.value) {
//             return { valid: false, message: `❌ Vui lòng chọn Đơn vị vận chuyển.` };
//         }
        
//         return { valid: true };
//     }

//     validateQuantityRequirement() {
//         for (const row of document.querySelectorAll('#billTable tbody tr')) {
//             const billIdInput = row.querySelector('.bill-id-input');
//             const quantityInput = row.querySelector('.quantity-input');
            
//             if (billIdInput?.value.trim() && quantityInput) {
//                  const quantity = parseInt(quantityInput.value, 10);
//                  if (isNaN(quantity) || quantity <= 0) {
//                      return { valid: false, message: `❌ Bill ID "${billIdInput.value}" phải có số lượng bao/tải lớn hơn 0.` };
//                  }
//             }
//         }
//         return { valid: true };
//     }

//     generateGroupId(billIds) {
//         return billIds.join('_');
//     }

//     async submitBulkForm() {
//         const resultContainer = document.getElementById('bulk-result-container');
//         const submitBtn = document.getElementById('submitBtn');
//         if (!resultContainer || !submitBtn) return;

//         resultContainer.innerHTML = '';
        
//         if (this.hasInvalidIds()) {
//             resultContainer.innerHTML = '<div class="error">Vui lòng sửa các Bill ID không hợp lệ trước khi lưu.</div>';
//             return;
//         }

//         const requiredValidation = this.validateRequiredFields();
//         if (!requiredValidation.valid) {
//             resultContainer.innerHTML = `<div class="error">${requiredValidation.message}</div>`;
//             return;
//         }

//         const quantityValidation = this.validateQuantityRequirement();
//         if (!quantityValidation.valid) {
//             resultContainer.innerHTML = `<div class="error">${quantityValidation.message}</div>`;
//             return;
//         }
        
//         const billData = [];
//         const groupQuantities = {};
//         const groupBillIds = {}; // ✅ THÊM: Track Bill IDs của từng group
//         const processedGroups = new Set();

//         // Lấy số lượng của từng nhóm
//         document.querySelectorAll('tr.grouped-row .quantity-input').forEach(input => {
//             const row = input.closest('tr');
//             const groupId = row.dataset.groupId;
//             groupQuantities[groupId] = parseInt(input.value, 10) || 0;
//         });

//         // ✅ THÊM: Thu thập Bill IDs cho từng group
//         document.querySelectorAll('#billTable tbody tr.grouped-row').forEach(row => {
//             const billId = row.querySelector('.bill-id-input')?.value.trim();
//             if (billId) {
//                 const groupId = row.dataset.groupId;
//                 if (!groupBillIds[groupId]) {
//                     groupBillIds[groupId] = [];
//                 }
//                 groupBillIds[groupId].push(billId);
//             }
//         });

//         // ✅ SỬA: Thu thập dữ liệu từ tất cả các dòng với Group ID
//         document.querySelectorAll('#billTable tbody tr').forEach(row => {
//             const billId = row.querySelector('.bill-id-input')?.value.trim();
//             if (billId) {
//                 const bagQuantity = parseInt(row.querySelector('.bag-quantity-input')?.value, 10) || 0;
//                 let quantity = 0;
//                 let groupId = null; // ✅ THÊM: Group ID field

//                 if (row.classList.contains('single-row')) {
//                     quantity = parseInt(row.querySelector('.quantity-input').value, 10) || 0;
//                     // Single row không có Group ID
//                 } else if (row.classList.contains('grouped-row')) {
//                     const rowGroupId = row.dataset.groupId;
//                     quantity = groupQuantities[rowGroupId] || 0;
                    
//                     // ✅ THÊM: Tạo Group ID từ Bill IDs bằng cách nối với _
//                     if (groupBillIds[rowGroupId] && groupBillIds[rowGroupId].length > 0) {
//                         groupId = groupBillIds[rowGroupId].join('_');
//                     }
//                 }

//                 billData.push({ 
//                     bill_id: billId, 
//                     bag_quantity: bagQuantity,
//                     quantity,
//                     group_id: groupId // ✅ THÊM: Group ID
//                 });
//             }
//         });

//         if (billData.length === 0) {
//             resultContainer.innerHTML = '<div class="error">Vui lòng nhập ít nhất một Bill ID.</div>';
//             return;
//         }
        
//         submitBtn.classList.add('htmx-request');
//         resultContainer.innerHTML = '<div class="info">🔄 Đang xử lý, vui lòng chờ...</div>';
        
//         // ✅ SỬA: Sử dụng class selector thay vì name attribute
//         const depotInputs = document.querySelectorAll('.depot-hidden-input');
//         const handoverPersonInput = document.querySelector('.employee-hidden-input');
//         const transportProviderInput = document.querySelector('.transport-hidden-input');
        
//         const payload = {
//             from_depot: depotInputs[0]?.value || '',
//             to_depot: depotInputs[1]?.value || '',
//             handover_person: handoverPersonInput?.value || '',
//             transport_provider: transportProviderInput?.value || '',
//             bill_data: billData
//         };
        
//         try {
//             const response = await fetch('/bulk-create-records', {
//                 method: 'POST',
//                 headers: {'Content-Type': 'application/json'},
//                 body: JSON.stringify(payload)
//             });
//             const resultHTML = await response.text();
//             resultContainer.innerHTML = resultHTML;
            
//             if (response.ok && resultHTML.includes('success')) {
//                 // Xóa bảng và thêm lại một dòng mới
//                 const tbody = document.querySelector('#billTable tbody');
//                 if (tbody) tbody.innerHTML = '';
//                 this.addSingleBillRow();
//             }
//         } catch (error) {
//             resultContainer.innerHTML = `<div class="error">Lỗi kết nối đến máy chủ: ${error.message}</div>`;
//         } finally {
//             submitBtn.classList.remove('htmx-request');
//         }
//     }

    
// }

// export default BulkFormManager;


// static/js/bulk-form.js
import { showValidationError } from './validators.js';

class BulkFormManager {
    constructor() {
        this.rowCounter = 0;
        this.groupCounter = 0;
        this.lastFromDepotValue = '';
        this.lastToDepotValue = '';
        this.revalidateTimeout = null;

        this.bindGlobalMethods();
        this.setupCommonFieldsWatcher();
    }
    
    bindGlobalMethods() {
        // Gắn các phương thức vào window để HTML có thể gọi qua onclick
        window.addSingleBillRow = this.addSingleBillRow.bind(this);
        window.showGroupedBillModal = this.showGroupedBillModal.bind(this);
        window.closeGroupedBillModal = this.closeGroupedBillModal.bind(this);
        window.addGroupedBillRows = this.addGroupedBillRows.bind(this);
        window.removeBillRow = this.removeBillRow.bind(this);
        window.removeGroupedRows = this.removeGroupedRows.bind(this);
        window.validateBillId = this.validateBillId.bind(this);
        window.submitBulkForm = this.submitBulkForm.bind(this);
        window.updateTotalSummary = this.updateTotalSummary.bind(this);

        // Các phương thức của Modal
        window.addModalBillRow = this.addModalBillRow.bind(this);
        window.removeModalBillRow = this.removeModalBillRow.bind(this);
        window.validateModalBillId = this.validateModalBillId.bind(this);
    }

    setupCommonFieldsWatcher() {
        const depotInputs = document.querySelectorAll('.depot-hidden-input');
        const fromDepotInput = depotInputs[0];
        const toDepotInput = depotInputs[1];
        this.lastFromDepotValue = fromDepotInput ? fromDepotInput.value : '';
        this.lastToDepotValue = toDepotInput ? toDepotInput.value : '';

        setInterval(() => this.checkForValueChanges(), 800);
    }

    checkForValueChanges() {
        const depotInputs = document.querySelectorAll('.depot-hidden-input');
        const fromDepotInput = depotInputs[0];
        const toDepotInput = depotInputs[1];

        if (fromDepotInput && fromDepotInput.value !== this.lastFromDepotValue) {
            this.lastFromDepotValue = fromDepotInput.value;
            this.debounceRevalidate();
        }
        if (toDepotInput && toDepotInput.value !== this.lastToDepotValue) {
            this.lastToDepotValue = toDepotInput.value;
            this.debounceRevalidate();
        }
    }

    debounceRevalidate() {
        clearTimeout(this.revalidateTimeout);
        this.revalidateTimeout = setTimeout(() => this.revalidateAllBillIds(), 500);
    }

    async revalidateAllBillIds() {
        const billIdInputs = document.querySelectorAll('.bill-id-input');
        for (const input of billIdInputs) {
            if (input.value.trim()) {
                await this.validateBillId(input);
            }
        }
    }

    addSingleBillRow() {
        const tbody = document.querySelector('#billTable tbody');
        if (!tbody) return;
        this.rowCounter++;
        const row = document.createElement('tr');
        row.id = `row-${this.rowCounter}`;
        row.classList.add('single-row');
        // ========================================================
        // === ✅ ĐÃ CHỈNH SỬA TẠI ĐÂY ===
        // ========================================================
        row.innerHTML = `
            <td><input type="text" class="form-control bill-id-input" placeholder="ID" onblur="validateBillId(this)"></td>
            <td><input type="number" class="form-control bag-quantity-input" placeholder="SL bao" min="0" oninput="updateTotalSummary()"></td>
            <td><input type="number" class="form-control quantity-input" placeholder="SL tải" min="1" required oninput="updateTotalSummary()"></td>
            <td class="status-cell"><span class="status-pending">⏳ Chưa kiểm tra</span></td>
            <td class="action-cell"><button type="button" class="btn btn-danger btn-small" onclick="removeBillRow('${row.id}')">🗑️</button></td>
        `;
        tbody.appendChild(row);
        this.updateTotalSummary();
    }

    addModalBillRow() {
        const modalTbody = document.getElementById('modalBillTbody');
        if (!modalTbody) return;
        
        const newRow = modalTbody.insertRow();
        newRow.innerHTML = `
            <td><input type="text" class="form-control modal-bill-id-input" placeholder="ID" onblur="validateModalBillId(this)"></td>
            <td class="status-cell"><span class="status-pending">⏳ Chưa kiểm tra</span></td>
            <td class="action-cell"><button type="button" class="btn btn-danger btn-small" onclick="removeModalBillRow(this)">🗑️</button></td>
        `;
        const newInput = newRow.querySelector('input');
        if (newInput) {
            newInput.focus();
        }
    }

    removeModalBillRow(button) {
        const row = button.closest('tr');
        if (row) {
            row.remove();
        }
    }

    async validateModalBillId(input) {
        const billId = input.value.trim();
        const row = input.closest('tr');
        const statusCell = row.querySelector('.status-cell');
        
        if (!billId) {
            statusCell.innerHTML = '<span class="status-pending">⏳ Chưa kiểm tra</span>';
            return;
        }

        const depotInputs = document.querySelectorAll('.depot-hidden-input');
        const fromDepot = depotInputs[0]?.value || '';
        const toDepot = depotInputs[1]?.value || '';
        
        if (!fromDepot || !toDepot) {
            statusCell.innerHTML = '<span class="status-invalid" title="Vui lòng chọn Kho đi và Kho đến ở form chính trước.">❌ Chọn kho trước</span>';
            return;
        }

        statusCell.innerHTML = '<span class="status-checking">🔄 Đang KT...</span>';
        
        try {
            const response = await fetch('/validate-bill-id', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `bill_id=${billId}&from_depot=${fromDepot}&to_depot=${toDepot}`
            });
            const result = await response.json();
            
            if (result.valid) {
                statusCell.innerHTML = '<span class="status-valid">✅ Hợp lệ</span>';
            } else {
                statusCell.innerHTML = `<span class="status-invalid" title="${result.message}">❌ ${result.message}</span>`;
            }
        } catch (error) {
            statusCell.innerHTML = '<span class="status-error" title="Lỗi kết nối máy chủ.">⚠️ Lỗi</span>';
        }
    }

    showGroupedBillModal() {
        const modal = document.getElementById('groupedBillModal');
        const modalTbody = document.getElementById('modalBillTbody');
        
        if (!modal) return;

        if (modalTbody) {
            modalTbody.innerHTML = ''; 
            this.addModalBillRow();
            this.addModalBillRow();
        }

        modal.classList.add('show');
        
        setTimeout(() => {
            const firstInput = modalTbody?.querySelector('input');
            if (firstInput) firstInput.focus();
        }, 100);
    }

    closeGroupedBillModal() {
        const modal = document.getElementById('groupedBillModal');
        if (modal) modal.classList.remove('show');
    }

    addGroupedBillRows() {
        const modalInputs = document.querySelectorAll('#modalBillTbody .modal-bill-id-input');
        const billIds = Array.from(modalInputs).map(input => input.value.trim()).filter(id => id);

        if (billIds.length < 2) {
            alert('Vui lòng nhập ít nhất 2 Bill ID để gộp thành một tải.');
            return;
        }

        const invalidBill = Array.from(modalInputs).find(input => {
            const row = input.closest('tr');
            return row && row.querySelector('.status-invalid');
        });
        
        if (invalidBill) {
            alert('Tồn tại Bill ID không hợp lệ trong danh sách. Vui lòng kiểm tra lại.');
            return;
        }
        
        const tbody = document.querySelector('#billTable tbody');
        if (!tbody) return;

        this.groupCounter++;
        const groupId = `group-${this.groupCounter}`;
        const groupQuantity = 1;

        billIds.forEach((billId, index) => {
            this.rowCounter++;
            const row = document.createElement('tr');
            row.id = `row-${this.rowCounter}`;
            row.classList.add('grouped-row');
            row.dataset.groupId = groupId;
            
            let rowHtml = `<td><input type="text" class="form-control bill-id-input" value="${billId}" onblur="validateBillId(this)" readonly></td>`;
            
            // ========================================================
            // === ✅ ĐÃ CHỈNH SỬA TẠI ĐÂY ===
            // ========================================================
            rowHtml += `<td><input type="number" class="form-control bag-quantity-input" placeholder="SL bao" min="0" oninput="updateTotalSummary()"></td>`;
            
            if (index === 0) {
                rowHtml += `
                    <td rowspan="${billIds.length}" class="grouped-quantity-cell">
                        <input type="number" class="form-control quantity-input" value="${groupQuantity}" min="1" required oninput="updateTotalSummary()">
                        <small class="text-muted">${billIds.length} ID</small>
                    </td>
                `;
            }
            
            rowHtml += `<td class="status-cell"><span class="status-valid">✅ Hợp lệ</span></td>`;
            
            if (index === 0) {
                rowHtml += `<td rowspan="${billIds.length}" class="action-cell"><button type="button" class="btn btn-danger btn-small" onclick="removeGroupedRows('${groupId}')" title="Xóa nhóm">🗑️</button></td>`;
            }
            
            row.innerHTML = rowHtml;
            tbody.appendChild(row);
        });

        this.closeGroupedBillModal();
        this.updateTotalSummary();
    }

    removeBillRow(rowId) {
        const row = document.getElementById(rowId);
        if (row) {
            row.remove();
            this.updateTotalSummary();
        }
    }

    removeGroupedRows(groupId) {
        document.querySelectorAll(`tr[data-group-id="${groupId}"]`).forEach(row => row.remove());
        this.updateTotalSummary();
    }

    async validateBillId(input) {
        await this.validateModalBillId(input);
    }

    // ========================================================
    // === ✅ ĐÃ CHỈNH SỬA TẠI ĐÂY ===
    // ========================================================
    updateTotalSummary() {
        let totalBills = 0;
        let totalBags = 0;
        let totalLoads = 0;
        
        document.querySelectorAll('#billTable tbody tr').forEach(row => {
            if (row.querySelector('.bill-id-input')?.value.trim()) {
                totalBills++;
            }

            const bagInput = row.querySelector('.bag-quantity-input');
            if (bagInput) {
                totalBags += parseInt(bagInput.value, 10) || 0;
            }

            if (row.querySelector('.quantity-input')) {
                const quantity = parseInt(row.querySelector('.quantity-input').value, 10) || 0;
                totalLoads += quantity;
            }
        });
        
        const totalBillsSpan = document.getElementById('totalBills');
        const totalBagsSpan = document.getElementById('totalBags');
        const totalLoadsSpan = document.getElementById('totalLoads');

        if(totalBillsSpan) totalBillsSpan.textContent = totalBills;
        if(totalBagsSpan) totalBagsSpan.textContent = totalBags;
        if(totalLoadsSpan) totalLoadsSpan.textContent = totalLoads;
    }

    hasInvalidIds() {
        return document.querySelectorAll('#billTable .status-invalid').length > 0;
    }

    validateRequiredFields() {
        const depotInputs = document.querySelectorAll('.depot-hidden-input');
        const fromDepot = depotInputs[0]?.value || '';
        const toDepot = depotInputs[1]?.value || '';
        
        const handoverPersonInput = document.querySelector('.employee-hidden-input');
        const transportProviderInput = document.querySelector('.transport-hidden-input');
        
        if (!fromDepot) {
            return { valid: false, message: `❌ Vui lòng chọn Kho đi.` };
        }
        if (!toDepot) {
            return { valid: false, message: `❌ Vui lòng chọn Kho đến.` };
        }
        if (!handoverPersonInput?.value) {
            return { valid: false, message: `❌ Vui lòng chọn Người bàn giao.` };
        }
        if (!transportProviderInput?.value) {
            return { valid: false, message: `❌ Vui lòng chọn Đơn vị vận chuyển.` };
        }
        
        return { valid: true };
    }

    validateQuantityRequirement() {
        for (const row of document.querySelectorAll('#billTable tbody tr')) {
            const billIdInput = row.querySelector('.bill-id-input');
            const quantityInput = row.querySelector('.quantity-input');
            
            if (billIdInput?.value.trim() && quantityInput) {
                 const quantity = parseInt(quantityInput.value, 10);
                 if (isNaN(quantity) || quantity <= 0) {
                     return { valid: false, message: `❌ Bill ID "${billIdInput.value}" phải có số lượng bao/tải lớn hơn 0.` };
                 }
            }
        }
        return { valid: true };
    }

    generateGroupId(billIds) {
        return billIds.join('_');
    }

    async submitBulkForm() {
        const resultContainer = document.getElementById('bulk-result-container');
        const submitBtn = document.getElementById('submitBtn');
        if (!resultContainer || !submitBtn) return;

        resultContainer.innerHTML = '';
        
        if (this.hasInvalidIds()) {
            resultContainer.innerHTML = '<div class="error">Vui lòng sửa các Bill ID không hợp lệ trước khi lưu.</div>';
            return;
        }

        const requiredValidation = this.validateRequiredFields();
        if (!requiredValidation.valid) {
            resultContainer.innerHTML = `<div class="error">${requiredValidation.message}</div>`;
            return;
        }

        const quantityValidation = this.validateQuantityRequirement();
        if (!quantityValidation.valid) {
            resultContainer.innerHTML = `<div class="error">${quantityValidation.message}</div>`;
            return;
        }
        
        const billData = [];
        const groupQuantities = {};
        const groupBillIds = {}; 
        const processedGroups = new Set();

        document.querySelectorAll('tr.grouped-row .quantity-input').forEach(input => {
            const row = input.closest('tr');
            const groupId = row.dataset.groupId;
            groupQuantities[groupId] = parseInt(input.value, 10) || 0;
        });

        document.querySelectorAll('#billTable tbody tr.grouped-row').forEach(row => {
            const billId = row.querySelector('.bill-id-input')?.value.trim();
            if (billId) {
                const groupId = row.dataset.groupId;
                if (!groupBillIds[groupId]) {
                    groupBillIds[groupId] = [];
                }
                groupBillIds[groupId].push(billId);
            }
        });

        document.querySelectorAll('#billTable tbody tr').forEach(row => {
            const billId = row.querySelector('.bill-id-input')?.value.trim();
            if (billId) {
                const bagQuantity = parseInt(row.querySelector('.bag-quantity-input')?.value, 10) || 0;
                let quantity = 0;
                let groupId = null;

                if (row.classList.contains('single-row')) {
                    quantity = parseInt(row.querySelector('.quantity-input').value, 10) || 0;
                } else if (row.classList.contains('grouped-row')) {
                    const rowGroupId = row.dataset.groupId;
                    quantity = groupQuantities[rowGroupId] || 0;
                    
                    if (groupBillIds[rowGroupId] && groupBillIds[rowGroupId].length > 0) {
                        groupId = groupBillIds[rowGroupId].join('_');
                    }
                }

                billData.push({ 
                    bill_id: billId, 
                    bag_quantity: bagQuantity,
                    quantity,
                    group_id: groupId
                });
            }
        });

        if (billData.length === 0) {
            resultContainer.innerHTML = '<div class="error">Vui lòng nhập ít nhất một Bill ID.</div>';
            return;
        }
        
        submitBtn.classList.add('htmx-request');
        resultContainer.innerHTML = '<div class="info">🔄 Đang xử lý, vui lòng chờ...</div>';
        
        const depotInputs = document.querySelectorAll('.depot-hidden-input');
        const handoverPersonInput = document.querySelector('.employee-hidden-input');
        const transportProviderInput = document.querySelector('.transport-hidden-input');
        
        const payload = {
            from_depot: depotInputs[0]?.value || '',
            to_depot: depotInputs[1]?.value || '',
            handover_person: handoverPersonInput?.value || '',
            transport_provider: transportProviderInput?.value || '',
            bill_data: billData
        };
        
        try {
            const response = await fetch('/bulk-create-records', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const resultHTML = await response.text();
            resultContainer.innerHTML = resultHTML;
            
            if (response.ok && resultHTML.includes('success')) {
                const tbody = document.querySelector('#billTable tbody');
                if (tbody) tbody.innerHTML = '';
                this.addSingleBillRow();
            }
        } catch (error) {
            resultContainer.innerHTML = `<div class="error">Lỗi kết nối đến máy chủ: ${error.message}</div>`;
        } finally {
            submitBtn.classList.remove('htmx-request');
        }
    }
}

export default BulkFormManager;