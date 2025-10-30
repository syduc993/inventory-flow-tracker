import { showValidationError } from './validators.js';

// --- HÀM HELPER CHO DEBOUNCE VÀ THROTTLE ---
function debounce(func, delay = 500) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

function throttle(func, limit = 250) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}


class BulkFormManager {
    constructor() {
        this.rowCounter = 0;
        this.groupCounter = 0;
        
        // --- BƯỚC 2.2 & 2.3: KHỞI TẠO CÁC HÀM ĐÃ TỐI ƯU HÓA ---
        this.throttledUpdateSummary = throttle(this.updateTotalSummary.bind(this), 250);
        this.debouncedValidateBillId = debounce(this.validateBillId.bind(this), 400);

        this.bindGlobalMethods();
        this.setupEventListeners();
    }
    
    bindGlobalMethods() {
        window.addSingleBillRow = this.addSingleBillRow.bind(this);
        window.showGroupedBillModal = this.showGroupedBillModal.bind(this);
        window.closeGroupedBillModal = this.closeGroupedBillModal.bind(this);
        window.addGroupedBillRows = this.addGroupedBillRows.bind(this);
        window.removeBillRow = this.removeBillRow.bind(this);
        window.removeGroupedRows = this.removeGroupedRows.bind(this);
        // validateBillId và updateTotalSummary không cần public nữa vì được gọi qua debounce/throttle
        window.submitBulkForm = this.submitBulkForm.bind(this);

        window.addModalBillRow = this.addModalBillRow.bind(this);
        window.removeModalBillRow = this.removeModalBillRow.bind(this);
        // Chúng ta vẫn cần hàm này cho modal
        window.validateModalBillId = this.validateModalBillId.bind(this);
    }

    setupEventListeners() {
        document.body.addEventListener('depotChanged', () => {
            this.revalidateAllBillIds();
        });
    }

    async revalidateAllBillIds() {
        const billIdInputs = document.querySelectorAll('.bill-id-input');
        for (const input of billIdInputs) {
            if (input.value.trim()) {
                await new Promise(resolve => setTimeout(resolve, 50)); 
                await this.validateBillId(input); // Gọi trực tiếp ở đây
            }
        }
    }
    
    // --- THAY ĐỔI LỚN: XÓA onblur, oninput và GẮN SỰ KIỆN BẰNG JS ---
    addSingleBillRow() {
        const tbody = document.querySelector('#billTable tbody');
        if (!tbody) return;
        this.rowCounter++;
        const row = document.createElement('tr');
        row.id = `row-${this.rowCounter}`;
        row.classList.add('single-row');

        // Xóa onblur và oninput khỏi HTML
        row.innerHTML = `
            <td><input type="text" class="form-control bill-id-input" placeholder="ID"></td>
            <td><input type="number" class="form-control quantity-input" placeholder="SL bao" min="1" required></td>
            <td><input type="number" class="form-control bag-quantity-input" placeholder="SL túi" min="0"></td>
            <td class="status-cell"><span class="status-pending">⏳ Chưa kiểm tra</span></td>
            <td class="action-cell"><button type="button" class="btn btn-danger btn-small">🗑️</button></td>
        `;

        // Gắn sự kiện bằng JavaScript
        const billIdInput = row.querySelector('.bill-id-input');
        const quantityInput = row.querySelector('.quantity-input');
        const bagQuantityInput = row.querySelector('.bag-quantity-input');
        const removeButton = row.querySelector('.btn-danger');

        billIdInput.addEventListener('input', (event) => {
            this.debouncedValidateBillId(event.target);
        });

        quantityInput.addEventListener('input', () => {
            this.throttledUpdateSummary();
        });

        bagQuantityInput.addEventListener('input', () => {
            this.throttledUpdateSummary();
        });

        removeButton.addEventListener('click', () => {
            this.removeBillRow(row.id);
        });

        tbody.appendChild(row);
        this.throttledUpdateSummary(); // Cập nhật tổng khi thêm dòng mới
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

    // validateModalBillId và validateBillId có thể gộp lại
    async validateBillId(inputElement) {
        const billId = inputElement.value.trim();
        const row = inputElement.closest('tr');
        if (!row) return;
        const statusCell = row.querySelector('.status-cell');
        
        if (!billId) {
            statusCell.innerHTML = '<span class="status-pending">⏳ Chưa kiểm tra</span>';
            return;
        }

        const toDepot = document.querySelector('.depot-hidden-input')?.value || '';
        if (!toDepot) {
            statusCell.innerHTML = '<span class="status-invalid" title="Vui lòng chọn Kho đến ở form chính trước.">❌ Chọn kho đến</span>';
            return;
        }

        statusCell.innerHTML = '<span class="status-checking">🔄 Đang KT...</span>';
        
        try {
            const response = await fetch('/validate-bill-id', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `bill_id=${billId}&to_depot=${toDepot}`
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
    
    async validateModalBillId(input) {
        // Hàm này vẫn dùng onblur cho đơn giản bên trong modal
        await this.validateBillId(input);
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
            
            let rowHtml = `<td><input type="text" class="form-control bill-id-input" value="${billId}" readonly></td>`;
            if (index === 0) {
                rowHtml += `
                    <td rowspan="${billIds.length}" class="grouped-quantity-cell">
                        <input type="number" class="form-control quantity-input" value="${groupQuantity}" min="1" required>
                        <small class="text-muted">${billIds.length} ID</small>
                    </td>
                `;
            }
            rowHtml += `<td><input type="number" class="form-control bag-quantity-input" placeholder="SL túi" min="0"></td>`;
            rowHtml += `<td class="status-cell"><span class="status-valid">✅ Hợp lệ</span></td>`;
            if (index === 0) {
                rowHtml += `<td rowspan="${billIds.length}" class="action-cell"><button type="button" class="btn btn-danger btn-small" title="Xóa nhóm">🗑️</button></td>`;
            }
            row.innerHTML = rowHtml;

            // Gắn sự kiện cho các input và button của grouped row
            row.querySelectorAll('.quantity-input, .bag-quantity-input').forEach(input => {
                input.addEventListener('input', () => this.throttledUpdateSummary());
            });
            row.querySelector('.bill-id-input')?.addEventListener('input', (e) => this.debouncedValidateBillId(e.target));
            row.querySelector('.btn-danger')?.addEventListener('click', () => this.removeGroupedRows(groupId));

            tbody.appendChild(row);
        });

        this.closeGroupedBillModal();
        this.throttledUpdateSummary();
    }

    removeBillRow(rowId) {
        const row = document.getElementById(rowId);
        if (row) {
            row.remove();
            this.throttledUpdateSummary();
        }
    }

    removeGroupedRows(groupId) {
        document.querySelectorAll(`tr[data-group-id="${groupId}"]`).forEach(row => row.remove());
        this.throttledUpdateSummary();
    }

    updateTotalSummary() {
        console.log("Updating summary..."); // Để kiểm tra throttle
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
        const toDepot = document.querySelector('.depot-hidden-input')?.value || '';
        const handoverPersonInput = document.querySelector('.employee-hidden-input');
        const transportProviderInput = document.querySelector('.transport-hidden-input');
        
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
                     return { valid: false, message: `❌ Bill ID "${billIdInput.value}" phải có số lượng bao lớn hơn 0.` };
                 }
            }
        }
        return { valid: true };
    }
    
    // ... các hàm còn lại giữ nguyên ...
    async submitBulkForm() {
        // Nội dung hàm này không thay đổi
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
            to_depot: depotInputs[0]?.value || '',
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