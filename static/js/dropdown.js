// static/js/dropdown.js - Dropdown Management
class DropdownManager {
    constructor() {
        this.initializeAll();
    }
    
    initializeAll() {
        this.initEmployeeDropdowns();
        this.initTransportDropdowns();
        this.initDepotDropdowns();
    }
    
    initializeNewDropdowns(container) {
        container.querySelectorAll('.employee-dropdown-component').forEach(this.initEmployeeDropdown.bind(this));
        container.querySelectorAll('.transport-dropdown-component').forEach(this.initTransportDropdown.bind(this));
        container.querySelectorAll('.depot-dropdown-component').forEach(this.initDepotDropdown.bind(this));
    }
    
    hideAllDropdowns() {
        // Employee và Depot dropdowns
        document.querySelectorAll('.employee-dropdown, .depot-dropdown').forEach(dd => {
            dd.style.display = 'none';
        });
        // Transport dropdowns
        document.querySelectorAll('.transport-dropdown').forEach(dd => {
            dd.classList.remove('show');
        });
    }
    
    initEmployeeDropdowns() {
        document.querySelectorAll('.employee-dropdown-component').forEach(this.initEmployeeDropdown.bind(this));
    }
    
    initTransportDropdowns() {
        document.querySelectorAll('.transport-dropdown-component').forEach(this.initTransportDropdown.bind(this));
    }
    
    initDepotDropdowns() {
        document.querySelectorAll('.depot-dropdown-component').forEach(this.initDepotDropdown.bind(this));
    }
    
    initEmployeeDropdown(component) {
        const searchInput = component.querySelector('.employee-search-input');
        const hiddenInput = component.querySelector('.employee-hidden-input');
        const dropdown = component.querySelector('.employee-dropdown');
        const options = dropdown.querySelectorAll('.employee-option');
        const infoDiv = dropdown.querySelector('.employee-dropdown-info');

        if (!searchInput || !hiddenInput || !dropdown || !infoDiv) return;
        
        dropdown.style.display = 'none';
        
        // ✅ SỬA: Show existing value khi focus lại
        if (hiddenInput.value) {
            const selectedOption = dropdown.querySelector(`[data-value="${hiddenInput.value}"]`);
            if (selectedOption) {
                const employeeName = selectedOption.dataset.name;
                const employeeId = selectedOption.dataset.value;
                searchInput.value = `${employeeName} (${employeeId})`;
                selectedOption.classList.add('selected');
            }
        }
        
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim().toLowerCase();
            
            if (query.length < 1) {
                dropdown.style.display = 'none';
                hiddenInput.value = '';
                return;
            }
            
            dropdown.style.display = 'block';
            this.filterEmployees(query, options, infoDiv);
        });

        // ✅ SỬA: Ngăn người dùng nhập tự do - chỉ cho phép chọn từ dropdown
        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                if (searchInput.value.trim() && !hiddenInput.value) {
                    searchInput.value = '';
                    this.showValidationError('Vui lòng chọn nhân viên từ danh sách');
                }
                dropdown.style.display = 'none';
            }, 200);
        });

        // ✅ SỬA: Show giá trị đã chọn khi focus lại
        searchInput.addEventListener('focus', () => {
            if (hiddenInput.value) {
                // Nếu đã có giá trị được chọn, hiển thị dropdown với giá trị đó
                dropdown.style.display = 'block';
                this.filterEmployees(searchInput.value.toLowerCase(), options, infoDiv);
            } else {
                const query = searchInput.value.trim().toLowerCase();
                if (query.length >= 1) {
                    dropdown.style.display = 'block';
                    this.filterEmployees(query, options, infoDiv);
                }
            }
        });

        dropdown.addEventListener('click', (e) => {
            const option = e.target.closest('.employee-option');
            if (option) {
                const employeeId = option.dataset.value;
                const employeeName = option.dataset.name;

                searchInput.value = `${employeeName} (${employeeId})`;
                hiddenInput.value = employeeId;
                dropdown.style.display = 'none';

                options.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
            }
        });

        // ✅ SỬA: Ngăn người dùng typing sau khi đã chọn
        searchInput.addEventListener('keydown', (e) => {
            // Nếu đã có giá trị selected và người dùng gõ thêm, clear selection
            if (hiddenInput.value && e.key !== 'Tab' && e.key !== 'Enter') {
                if (e.key === 'Backspace' || e.key === 'Delete' || e.key.length === 1) {
                    hiddenInput.value = '';
                    options.forEach(opt => opt.classList.remove('selected'));
                }
            }
        });
    }
    
    initTransportDropdown(component) {
        const searchInput = component.querySelector('.transport-search-input');
        const hiddenInput = component.querySelector('.transport-hidden-input');
        const dropdown = component.querySelector('.transport-dropdown');
        const options = dropdown.querySelectorAll('.transport-option');
        const infoDiv = dropdown.querySelector('.transport-dropdown-info');

        if (!searchInput || !hiddenInput || !dropdown || !infoDiv) return;
        
        dropdown.classList.remove('show');
        
        // ✅ SỬA: Show existing value khi focus lại
        if (hiddenInput.value) {
            const selectedOption = dropdown.querySelector(`[data-value="${hiddenInput.value}"]`);
            if (selectedOption) {
                searchInput.value = selectedOption.dataset.name;
                selectedOption.classList.add('selected');
            }
        }
        
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim().toLowerCase();
            
            if (query.length < 1) {
                dropdown.classList.remove('show');
                hiddenInput.value = '';
                return;
            }
            
            dropdown.classList.add('show');
            this.filterTransportProviders(query, options, infoDiv);
        });

        // ✅ SỬA: Ngăn người dùng nhập tự do
        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                if (searchInput.value.trim() && !hiddenInput.value) {
                    searchInput.value = '';
                    this.showValidationError('Vui lòng chọn đơn vị vận chuyển từ danh sách');
                }
                dropdown.classList.remove('show');
            }, 200);
        });

        // ✅ SỬA: Show giá trị đã chọn khi focus lại
        searchInput.addEventListener('focus', () => {
            if (hiddenInput.value) {
                dropdown.classList.add('show');
                this.filterTransportProviders(searchInput.value.toLowerCase(), options, infoDiv);
            } else {
                const query = searchInput.value.trim().toLowerCase();
                if (query.length >= 1) {
                    dropdown.classList.add('show');
                    this.filterTransportProviders(query, options, infoDiv);
                }
            }
        });

        dropdown.addEventListener('click', (e) => {
            const option = e.target.closest('.transport-option');
            if (option) {
                const providerId = option.dataset.value;
                const providerName = option.dataset.name;

                searchInput.value = providerName;
                hiddenInput.value = providerId;
                dropdown.classList.remove('show');

                options.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
            }
        });

        // ✅ SỬA: Ngăn người dùng typing sau khi đã chọn
        searchInput.addEventListener('keydown', (e) => {
            if (hiddenInput.value && e.key !== 'Tab' && e.key !== 'Enter') {
                if (e.key === 'Backspace' || e.key === 'Delete' || e.key.length === 1) {
                    hiddenInput.value = '';
                    options.forEach(opt => opt.classList.remove('selected'));
                }
            }
        });
    }


    initDepotDropdown(component) {
        const searchInput = component.querySelector('.depot-search-input');
        const hiddenInput = component.querySelector('.depot-hidden-input');
        const dropdown = component.querySelector('.depot-dropdown');
        const options = dropdown.querySelectorAll('.depot-option');
        const infoDiv = dropdown.querySelector('.depot-dropdown-info');

        if (!searchInput || !hiddenInput || !dropdown || !infoDiv) return;
        
        dropdown.style.display = 'none';
        
        if (hiddenInput.value) {
            const selectedOption = dropdown.querySelector(`[data-value="${hiddenInput.value}"]`);
            if (selectedOption) {
                searchInput.value = selectedOption.dataset.name;
                selectedOption.classList.add('selected');
            }
        }
        
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim().toLowerCase();
            
            if (query.length < 1) {
                dropdown.style.display = 'none';
                hiddenInput.value = '';
                return;
            }
            
            dropdown.style.display = 'block';
            this.filterDepots(query, options, infoDiv);
        });

        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                if (searchInput.value.trim() && !hiddenInput.value) {
                    searchInput.value = '';
                    this.showValidationError('Vui lòng chọn depot từ danh sách');
                }
                dropdown.style.display = 'none';
            }, 200);
        });

        searchInput.addEventListener('focus', () => {
            if (hiddenInput.value) {
                dropdown.style.display = 'block';
                this.filterDepots(searchInput.value.toLowerCase(), options, infoDiv);
            } else {
                const query = searchInput.value.trim().toLowerCase();
                if (query.length >= 1) {
                    dropdown.style.display = 'block';
                    this.filterDepots(query, options, infoDiv);
                }
            }
        });

        dropdown.addEventListener('click', (e) => {
            const option = e.target.closest('.depot-option');
            if (option) {
                const depotId = option.dataset.value;
                const depotName = option.dataset.name;
                const previousValue = hiddenInput.value;

                searchInput.value = depotName;
                hiddenInput.value = depotId;
                dropdown.style.display = 'none';

                options.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');

                // --- THAY ĐỔI QUAN TRỌNG ---
                // Chỉ phát sự kiện nếu giá trị thực sự thay đổi.
                if (previousValue !== depotId) {
                    console.log(`Depot changed to: ${depotId}. Firing depotChanged event.`);
                    const depotChangedEvent = new CustomEvent('depotChanged', {
                        detail: {
                            depotId: depotId,
                            depotName: depotName
                        }
                    });
                    document.body.dispatchEvent(depotChangedEvent);
                }
                // --- KẾT THÚC THAY ĐỔI ---
            }
        });

        searchInput.addEventListener('keydown', (e) => {
            if (hiddenInput.value && e.key !== 'Tab' && e.key !== 'Enter') {
                if (e.key === 'Backspace' || e.key === 'Delete' || e.key.length === 1) {
                    hiddenInput.value = '';
                    options.forEach(opt => opt.classList.remove('selected'));
                }
            }
        });
    }

    
    filterEmployees(query, options, infoDiv) {
        let visibleCount = 0;
        const maxResults = 5;
        
        options.forEach(option => {
            const name = option.dataset.name.toLowerCase();
            const id = option.dataset.value.toLowerCase();
            const department = option.dataset.department.toLowerCase();
            
            const isMatch = name.includes(query) || id.includes(query) || department.includes(query);
            
            if (isMatch && visibleCount < maxResults) {
                option.style.display = 'block';
                visibleCount++;
            } else {
                option.style.display = 'none';
            }
        });
        
        this.updateInfoDiv(infoDiv, visibleCount, maxResults);
    }
    
    filterTransportProviders(query, options, infoDiv) {
        let visibleCount = 0;
        const maxResults = 5;
        
        options.forEach(option => {
            const name = option.dataset.name.toLowerCase();
            const isMatch = name.includes(query);
            
            if (isMatch && visibleCount < maxResults) {
                option.style.display = 'block';
                visibleCount++;
            } else {
                option.style.display = 'none';
            }
        });
        
        this.updateInfoDiv(infoDiv, visibleCount, maxResults);
    }
    
    filterDepots(query, options, infoDiv) {
        let visibleCount = 0;
        const maxResults = 5;
        
        options.forEach(option => {
            const name = option.dataset.name.toLowerCase();
            const code = option.dataset.code.toLowerCase();
            const address = option.dataset.address.toLowerCase();
            
            const isMatch = name.includes(query) || code.includes(query) || address.includes(query);
            
            if (isMatch && visibleCount < maxResults) {
                option.style.display = 'block';
                visibleCount++;
            } else {
                option.style.display = 'none';
            }
        });
        
        this.updateInfoDiv(infoDiv, visibleCount, maxResults);
    }
    
    updateInfoDiv(infoDiv, visibleCount, maxResults) {
        if (visibleCount === 0) {
            infoDiv.innerHTML = '<small style="color: #c62828;">Không tìm thấy kết quả phù hợp</small>';
        } else if (visibleCount >= maxResults) {
            infoDiv.innerHTML = `<small>Hiển thị ${maxResults} kết quả đầu tiên. Gõ thêm để thu hẹp.</small>`;
        } else {
            infoDiv.innerHTML = `<small>Tìm thấy ${visibleCount} kết quả</small>`;
        }
    }

    // ✅ THÊM: Helper method để show validation error
    showValidationError(message) {
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
}

export default DropdownManager;
