# FILE: src/utils/larkbase.py

import requests
import logging

# Thiết lập logging cơ bản
logging.basicConfig(level=logging.INFO)

API_ENDPOINT = 'https://open.larksuite.com/open-apis'
API_HOST = "https://open.larksuite.com/open-apis/bitable/v1/apps"

def larkbase_get_token(app_id=None, app_secret=None, endpoint=API_ENDPOINT):
    APP_ID = app_id or 'cli_a7fab27260385010'
    APP_SECRET = app_secret or 'Zg4MVcFfiOu0g09voTcpfd4WGDpA0Ly5'
    url = f"{endpoint}/auth/v3/tenant_access_token/internal"
    try:
        resp = requests.post(url, json={'app_id': APP_ID, 'app_secret': APP_SECRET})
        if resp.status_code == 200:
            data = resp.json()
            if data.get('code') == 0:
                return data['tenant_access_token']
    except Exception as e:
        logging.error(f"Lỗi khi lấy token: {e}")
    return None

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def larkbase_get_all(app_token, table_id):
    token = larkbase_get_token()
    if not token:
        logging.error("Không xác thực được với Larkbase.")
        return []

    all_records = []
    page_token = ""
    while True:
        try:
            url = f"{API_HOST}/{app_token}/tables/{table_id}/records?page_size=500"
            if page_token:
                url += f"&page_token={page_token}"
            
            resp = requests.get(url, headers=get_headers(token))
            if resp.status_code != 200:
                logging.error(f"API trả về status code: {resp.status_code}")
                break
            
            res_data = resp.json()
            if res_data.get("code") != 0:
                logging.error(f"API trả về code: {res_data.get('code')}, msg: {res_data.get('msg', '')}")
                break

            data = res_data.get("data")
            if not data:  # ✅ Kiểm tra data trước
                break
                
            items = data.get("items", [])
            if not items:  # ✅ Kiểm tra items trước
                break
                
            all_records.extend(items)
            
            page_token = data.get("page_token", "")
            if not page_token:
                break
                
        except Exception as e:
            logging.error(f"Lỗi khi lấy dữ liệu: {e}")
            break
    return all_records

def larkbase_find_by_field(app_token, table_id, field, value):
    all_records = larkbase_get_all(app_token, table_id)
    if not all_records:
        # Trả về tuple (trạng thái, dữ liệu)
        return False, None
    for record in all_records:
        fields = record.get('fields', {})
        if str(fields.get(field, '')).strip() == str(value).strip():
            # Tìm thấy, trả về (True, record)
            return True, record
    # Không tìm thấy sau khi duyệt hết, trả về (False, None)
    return False, None

def larkbase_write_data(app_token, table_id, data):
    """Ghi dữ liệu mới và trả về (bool, message)"""
    token = larkbase_get_token()
    if not token:
        return False, "Không thể xác thực với Larkbase."
    try:
        url = f"{API_HOST}/{app_token}/tables/{table_id}/records"
        resp = requests.post(url, headers=get_headers(token), json={"fields": data})
        res_json = resp.json()
        if resp.status_code == 200 and res_json.get('code') == 0:
            return True, "Thêm mới thành công"
        else:
            error_msg = res_json.get('msg', resp.text)
            logging.error(f"Lỗi API khi ghi: {error_msg}")
            return False, error_msg
    except Exception as e:
        logging.error(f"Lỗi ngoại lệ khi ghi dữ liệu: {e}")
        return False, str(e)

def larkbase_update_data(app_token, table_id, record_id, data):
    """Cập nhật dữ liệu và trả về (bool, message)"""
    token = larkbase_get_token()
    if not token:
        return False, "Không thể xác thực với Larkbase."
    try:
        url = f"{API_HOST}/{app_token}/tables/{table_id}/records/{record_id}"
        resp = requests.put(url, headers=get_headers(token), json={"fields": data})
        res_json = resp.json()
        if resp.status_code == 200 and res_json.get('code') == 0:
            return True, "Cập nhật thành công"
        else:
            error_msg = res_json.get('msg', resp.text)
            logging.error(f"Lỗi API khi cập nhật: {error_msg}")
            return False, error_msg
    except Exception as e:
        logging.error(f"Lỗi ngoại lệ khi cập nhật: {e}")
        return False, str(e)

def larkbase_delete_record(app_token, table_id, record_id):
    """Xóa một bản ghi và trả về (bool, message)"""
    token = larkbase_get_token()
    if not token:
        return False, "Không thể xác thực với Larkbase."
    try:
        url = f"{API_HOST}/{app_token}/tables/{table_id}/records/{record_id}"
        resp = requests.delete(url, headers=get_headers(token))
        res_json = resp.json()
        if resp.status_code == 200 and res_json.get('code') == 0:
            return True, "Xóa thành công"
        else:
            error_msg = res_json.get('msg', resp.text)
            logging.error(f"Lỗi API khi xóa: {error_msg}")
            return False, error_msg
    except Exception as e:
        logging.error(f"Lỗi ngoại lệ khi xóa: {e}")
        return False, str(e)
