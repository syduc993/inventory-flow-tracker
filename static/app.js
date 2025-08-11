document.addEventListener('DOMContentLoaded', () => {

    // --- LOGIC CHO POPUP NOTIFICATION --- (Giữ nguyên, vẫn có thể hữu ích)
    function showNotification(message, type = 'success', duration = 3000) {
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

    // ✅ THÊM: Hàm hiển thị thông báo lỗi validation
    function showValidationError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'validation-error';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
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
    
    // --- LOGIC CẢI TIẾN CHO EMPLOYEE DROPDOWN ---
    function initEmployeeDropdown(component) {
        const searchInput = component.querySelector('.employee-search-input');
        const hiddenInput = component.querySelector('.employee-hidden-input');
        const dropdown = component.querySelector('.employee-dropdown');
        const options = dropdown.querySelectorAll('.employee-option');
        const infoDiv = dropdown.querySelector('.employee-dropdown-info');

        if (!searchInput || !hiddenInput || !dropdown || !infoDiv) return;
        
        // Ẩn dropdown ban đầu
        dropdown.style.display = 'none';
        
        // Hiển thị giá trị có sẵn (nếu đang edit)
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
            
            // Chỉ hiện dropdown khi gõ ít nhất 1 ký tự
            if (query.length < 1) {
                dropdown.style.display = 'none';
                hiddenInput.value = '';
                return;
            }
            
            dropdown.style.display = 'block';
            filterEmployees(query);
        });

        // ✅ SỬA: Thêm validation khi blur - chỉ chặn khi không hợp lệ
        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                // Nếu input có giá trị nhưng hiddenInput rỗng = nhập sai
                if (searchInput.value.trim() && !hiddenInput.value) {
                    searchInput.value = ''; // Reset input
                    showValidationError('Vui lòng chọn nhân viên từ danh sách');
                }
                dropdown.style.display = 'none';
            }, 200);
        });

        // Hiện dropdown khi focus vào input (nếu đã có nội dung)
        searchInput.addEventListener('focus', () => {
            const query = searchInput.value.trim().toLowerCase();
            if (query.length >= 1) {
                dropdown.style.display = 'block';
                filterEmployees(query);
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

                // Xóa class selected cũ và thêm cho option được chọn
                options.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
            }
        });
        
        function filterEmployees(query) {
            let visibleCount = 0;
            const maxResults = 5; // Giới hạn chỉ 5 kết quả
            
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
            
            // Cập nhật thông tin số kết quả
            if (visibleCount === 0) {
                infoDiv.innerHTML = '<small style="color: #c62828;">Không tìm thấy kết quả phù hợp</small>';
            } else if (visibleCount >= maxResults) {
                infoDiv.innerHTML = `<small>Hiển thị ${maxResults} kết quả đầu tiên. Gõ thêm để thu hẹp.</small>`;
            } else {
                infoDiv.innerHTML = `<small>Tìm thấy ${visibleCount} kết quả</small>`;
            }
        }
    }

    // --- LOGIC CHO TRANSPORT DROPDOWN (ĐÃ SỬA) ---
    function initTransportDropdown(component) {
        const searchInput = component.querySelector('.transport-search-input');
        const hiddenInput = component.querySelector('.transport-hidden-input');
        const dropdown = component.querySelector('.transport-dropdown');
        const options = dropdown.querySelectorAll('.transport-option');
        const infoDiv = dropdown.querySelector('.transport-dropdown-info');

        if (!searchInput || !hiddenInput || !dropdown || !infoDiv) return;
        
        // ✅ SỬA: Ẩn dropdown ban đầu bằng class
        dropdown.classList.remove('show');
        
        // Hiển thị giá trị có sẵn (nếu đang edit)
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
                dropdown.classList.remove('show'); // ✅ SỬA
                hiddenInput.value = '';
                return;
            }
            
            dropdown.classList.add('show'); // ✅ SỬA
            filterTransportProviders(query);
        });

        // ✅ SỬA: Thêm validation khi blur - chỉ chặn khi không hợp lệ
        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                // Nếu input có giá trị nhưng hiddenInput rỗng = nhập sai
                if (searchInput.value.trim() && !hiddenInput.value) {
                    searchInput.value = ''; // Reset input
                    showValidationError('Vui lòng chọn đơn vị vận chuyển từ danh sách');
                }
                dropdown.classList.remove('show');
            }, 200);
        });

        searchInput.addEventListener('focus', () => {
            const query = searchInput.value.trim().toLowerCase();
            if (query.length >= 1) {
                dropdown.classList.add('show'); // ✅ SỬA
                filterTransportProviders(query);
            }
        });

        dropdown.addEventListener('click', (e) => {
            const option = e.target.closest('.transport-option');
            if (option) {
                const providerId = option.dataset.value;
                const providerName = option.dataset.name;

                searchInput.value = providerName;
                hiddenInput.value = providerId;
                dropdown.classList.remove('show'); // ✅ SỬA

                options.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
            }
        });
        
        function filterTransportProviders(query) {
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
            
            if (visibleCount === 0) {
                infoDiv.innerHTML = '<small style="color: #c62828;">Không tìm thấy kết quả phù hợp</small>';
            } else if (visibleCount >= maxResults) {
                infoDiv.innerHTML = `<small>Hiển thị ${maxResults} kết quả đầu tiên. Gõ thêm để thu hẹp.</small>`;
            } else {
                infoDiv.innerHTML = `<small>Tìm thấy ${visibleCount} kết quả</small>`;
            }
        }
    }

    // Khởi tạo cho tất cả dropdown có sẵn khi tải trang
    document.querySelectorAll('.employee-dropdown-component').forEach(initEmployeeDropdown);
    document.querySelectorAll('.transport-dropdown-component').forEach(initTransportDropdown);

    // ✅ SỬA: Ẩn dropdown nếu click ra ngoài (tương thích cả hai phương pháp)
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.employee-search') && !e.target.closest('.transport-search')) {
            // Employee vẫn dùng style.display
            document.querySelectorAll('.employee-dropdown').forEach(dd => {
                dd.style.display = 'none';
            });
            // Transport dùng class
            document.querySelectorAll('.transport-dropdown').forEach(dd => {
                dd.classList.remove('show');
            });
        }
    });

    // --- XỬ LÝ HTMX RESPONSE ---
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.failed) {
            console.error("Yêu cầu HTMX thất bại:", evt.detail.xhr);
        }
    });
    
    // Khởi tạo lại JS cho dropdown khi HTMX swap nội dung mới vào
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        evt.detail.target.querySelectorAll('.employee-dropdown-component').forEach(initEmployeeDropdown);
        evt.detail.target.querySelectorAll('.transport-dropdown-component').forEach(initTransportDropdown);
    });
});
