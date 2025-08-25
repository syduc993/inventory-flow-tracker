# FILE: src/utils/transport_provider.py

from src.utils.larkbase import larkbase_get_all
import logging
import json
import os

# Cập nhật đường dẫn
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TRANSPORT_PROVIDERS_JSON_PATH = os.path.join(PROJECT_ROOT, "data", "transport_providers.json")


def get_transport_providers_from_larkbase(app_token, table_id="tblDefault"):
    """
    Lấy danh sách nhà cung cấp từ Larkbase
    """
    try:
        all_records = larkbase_get_all(app_token, table_id)
        if not all_records:
            logging.error("Không lấy được dữ liệu từ bảng nhà cung cấp")
            return []
        
        providers = []
        for record in all_records:
            fields = record.get('fields', {})
            provider_name = fields.get('Tên nhà cung cấp', '').strip()
            
            if provider_name:  # Chỉ lấy những record có tên
                providers.append({
                    "id": provider_name,  # Sử dụng tên làm ID
                    "name": provider_name
                })
        
        # Loại bỏ trùng lặp và sắp xếp
        unique_providers = []
        seen_names = set()
        
        for provider in providers:
            if provider['name'] not in seen_names:
                unique_providers.append(provider)
                seen_names.add(provider['name'])
        
        # Sắp xếp theo tên
        unique_providers.sort(key=lambda x: x['name'])
        
        return unique_providers
        
    except Exception as e:
        logging.error(f"Lỗi khi lấy danh sách nhà cung cấp: {e}")
        return []

def update_transport_providers_json_file(app_token, table_id="tblDefault"):
    """
    Cập nhật file JSON chứa danh sách nhà cung cấp
    """
    try:
        providers = get_transport_providers_from_larkbase(app_token, table_id)
        
        if not providers:
            return False, "Không lấy được danh sách nhà cung cấp từ Larkbase"
        
        # Ghi vào file JSON
        with open(TRANSPORT_PROVIDERS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(providers, f, ensure_ascii=False, indent=4)
        
        msg = f"Cập nhật thành công {len(providers)} nhà cung cấp"
        logging.info(msg)
        return True, msg
        
    except Exception as e:
        msg = f"Lỗi khi cập nhật file nhà cung cấp: {e}"
        logging.error(msg)
        return False, msg

def get_transport_providers_from_file():
    """
    Đọc danh sách nhà cung cấp từ file JSON
    """
    if not os.path.exists(TRANSPORT_PROVIDERS_JSON_PATH):
        logging.warning(f"File {TRANSPORT_PROVIDERS_JSON_PATH} không tồn tại.")
        return []
    
    try:
        with open(TRANSPORT_PROVIDERS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Lỗi khi đọc file {TRANSPORT_PROVIDERS_JSON_PATH}: {e}")
        return []
