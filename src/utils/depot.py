# FILE: src/utils/depot.py

import requests
import logging
import json
import os

# Cấu hình
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEPOT_JSON_PATH = os.path.join(PROJECT_ROOT, "depots.json")

# Thông tin API
DEPOT_API_URL = "https://pos.open.nhanh.vn/api/store/depot"
DEPOT_API_PARAMS = {
    'version': "2.0",
    'appId': "74951", 
    'businessId': "8901",
    'accessToken': "twf9P1xFZCUUgwt8zR0XgNeB6V5jsbq2KHb14bxovqK1ppCxyADwOK8FzQlCEeEGABRZINXoUCSzM50kjhwcrUSBWTY5nSvyhfnH2X2cI0pC7pNczSVxc1ratdDmxF85q7hUTUNCrUnpPTG5ZwLNO7bkMlEEJTCdPhgYaC"
}

def get_depots_from_api():
    """
    Lấy danh sách depot từ API Nhanh.vn
    """
    try:
        response = requests.post(DEPOT_API_URL, data=DEPOT_API_PARAMS, timeout=20)
        response.raise_for_status()
        
        json_data = response.json()
        if json_data.get("code") != 1:
            logging.error(f"API depot trả về code: {json_data.get('code')}")
            return []
        
        data = json_data.get("data", {})
        if not data:
            logging.warning("Không có dữ liệu depot từ API")
            return []
        
        depots = []
        for depot_info in data.values():
            depot_id = depot_info.get("id")
            depot_name = depot_info.get("name", "")
            depot_code = depot_info.get("code", "")
            
            if depot_id and depot_name:
                depots.append({
                    "id": str(depot_id),
                    "name": depot_name,
                    "code": depot_code,
                    "address": depot_info.get("address", "")
                })
        
        # Sắp xếp theo tên
        depots.sort(key=lambda x: x['name'])
        
        logging.info(f"Lấy thành công {len(depots)} depot từ API")
        return depots
        
    except Exception as e:
        logging.error(f"Lỗi khi lấy danh sách depot: {e}")
        return []

def update_depot_json_file():
    """
    Cập nhật file JSON chứa danh sách depot
    """
    try:
        depots = get_depots_from_api()
        
        if not depots:
            return False, "Không lấy được danh sách depot từ API"
        
        # Ghi vào file JSON
        with open(DEPOT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(depots, f, ensure_ascii=False, indent=4)
        
        msg = f"Cập nhật thành công! Đã lưu {len(depots)} depot vào file {DEPOT_JSON_PATH}."
        logging.info(msg)
        return True, msg
        
    except Exception as e:
        msg = f"Lỗi khi cập nhật file depot: {e}"
        logging.error(msg)
        return False, msg

def get_depots_from_file():
    """
    Đọc danh sách depot từ file JSON
    """
    if not os.path.exists(DEPOT_JSON_PATH):
        logging.warning(f"File {DEPOT_JSON_PATH} không tồn tại. Đang thử tạo lần đầu tiên...")
        success, message = update_depot_json_file()
        if not success:
            return []
    
    try:
        with open(DEPOT_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Lỗi khi đọc file {DEPOT_JSON_PATH}: {e}")
        return []
