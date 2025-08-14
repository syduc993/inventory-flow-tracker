# FILE: src/utils/cache.py

import requests
import logging
import json
import os

# --- CẤU HÌNH ---
PERSONNEL_API_BASE_URL = "https://minham.1office.vn/api/personnel/profile/gets?access_token=4467770316793457d8e1ad273033229"
EMPLOYEE_JSON_PATH = "employees.json" # File JSON sẽ được lưu ở thư mục gốc của dự án

logging.basicConfig(level=logging.INFO)

def update_employee_json_file():
    """
    Gọi API 1Office để lấy danh sách nhân viên đang hoạt động,
    bao gồm Mã NV và Phòng ban, sau đó lưu vào file employees.json.
    Trả về (bool, message).
    """
    logging.info("Bắt đầu quá trình cập nhật danh sách nhân viên từ 1Office...")
    all_employees_raw = []
    page = 1

    while True:
        url = f"{PERSONNEL_API_BASE_URL}&page={page}"
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            json_data = response.json()

            if not json_data or not json_data.get("data"):
                logging.info(f"Không có thêm dữ liệu ở trang {page}, dừng vòng lặp.")
                break

            current_page_data = json_data['data']
            all_employees_raw.extend(current_page_data)
            logging.info(f"Đã lấy thành công trang {page} với {len(current_page_data)} bản ghi.")
            page += 1
            # Thêm một khoảng nghỉ nhỏ để tránh gây quá tải cho API
            # time.sleep(0.1) 

        except requests.exceptions.RequestException as e:
            msg = f"Lỗi khi gọi API 1Office ở trang {page}: {e}"
            logging.error(msg)
            return False, msg
        except ValueError:
            msg = f"Lỗi: Không thể phân tích JSON từ API ở trang {page}."
            logging.error(msg)
            return False, msg

    # Lọc và định dạng lại dữ liệu, lấy thêm phòng ban
    active_employees = []
    for emp in all_employees_raw:
        # Chỉ lấy nhân viên đang hoạt động và có đủ thông tin cần thiết
        if emp.get("job_date_out") == "" and emp.get("code") and emp.get("name"):
            active_employees.append({
                "id": emp.get("code"),
                "name": emp.get("name"),
                "department": emp.get("department_id")
            })
    
    # Sắp xếp danh sách theo tên để dễ tìm kiếm
    active_employees.sort(key=lambda x: x['name'])

    # Ghi ra file JSON
    try:
        with open(EMPLOYEE_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(active_employees, f, ensure_ascii=False, indent=4)
        msg = f"Cập nhật thành công! Đã lưu {len(active_employees)} nhân viên vào file {EMPLOYEE_JSON_PATH}."
        logging.info(msg)
        return True, msg
    except IOError as e:
        msg = f"Lỗi khi ghi file {EMPLOYEE_JSON_PATH}: {e}"
        logging.error(msg)
        return False, msg


def get_employee_list_from_file():
    """
    Đọc danh sách nhân viên trực tiếp từ file employees.json.
    Nếu file không tồn tại, thử tạo nó lần đầu.
    """
    if not os.path.exists(EMPLOYEE_JSON_PATH):
        logging.warning(f"File {EMPLOYEE_JSON_PATH} không tồn tại. Đang thử tạo lần đầu tiên...")
        success, message = update_employee_json_file()
        if not success:
            # Nếu tạo file thất bại, trả về danh sách rỗng
            return []

    try:
        with open(EMPLOYEE_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Lỗi khi đọc hoặc phân tích file {EMPLOYEE_JSON_PATH}: {e}")
        return [] # Trả về rỗng nếu file bị lỗi
