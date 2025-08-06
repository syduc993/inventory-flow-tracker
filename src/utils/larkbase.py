import requests
import streamlit as st

API_ENDPOINT = 'https://open.larksuite.com/open-apis'
API_HOST = "https://open.larksuite.com/open-apis/bitable/v1/apps"

# Lấy access token (tự động lấy lại nếu có sẵn trong session)
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
        st.error(f"❌ Lỗi khi lấy token: {e}")
    return None

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

# --- READ ---

# Lấy toàn bộ record (với phân trang)
def larkbase_get_all(app_token, table_id):
    token = larkbase_get_token()
    if not token:
        st.error("❌ Không xác thực được với Larkbase.")
        return []

    all_records = []
    page_token = ""
    
    while True:
        try:
            url = f"{API_HOST}/{app_token}/tables/{table_id}/records?page_size=500"
            if page_token:
                url += f"&page_token={page_token}"
            
            resp = requests.get(url, headers=get_headers(token))
            
            # Kiểm tra status code trước
            if resp.status_code != 200:
                st.error(f"❌ API trả về status code: {resp.status_code}")
                break
            
            # Kiểm tra và parse JSON response
            try:
                res_data = resp.json()
            except Exception as e:
                st.error(f"❌ Lỗi parse JSON response: {e}")
                break
            
            # Kiểm tra response code
            if res_data.get("code") != 0:
                st.error(f"❌ API trả về code: {res_data.get('code')}, msg: {res_data.get('msg', '')}")
                break
            
            # Lấy data và items
            data = res_data.get("data", {})
            if data is None:
                st.error("❌ Response data is None")
                break
                
            items = data.get("items", [])
            if items is None:
                items = []
            
            # Extend records
            all_records.extend(items)
            
            # Kiểm tra page_token cho trang tiếp theo
            page_token = data.get("page_token", "")
            if not page_token or not items:
                break
                
        except Exception as e:
            st.error(f"❌ Lỗi khi lấy dữ liệu: {e}")
            break
    
    return all_records

# Tìm record theo (giá trị cột ID)
def larkbase_find_by_field(app_token, table_id, field, value):
    all_records = larkbase_get_all(app_token, table_id)
    if not all_records:
        return None
        
    # Nên kiểm tra field trùng tên cột đúng như Larkbase
    for record in all_records:
        fields = record.get('fields', {})
        if str(fields.get(field, '')).strip() == str(value).strip():
            return record
    return None

# --- CREATE ---
def larkbase_write_data(app_token, table_id, data):
    token = larkbase_get_token()
    if not token:
        st.error("❌ Không xác thực được với Larkbase.")
        return False

    try:
        url = f"{API_HOST}/{app_token}/tables/{table_id}/records"
        headers = get_headers(token)
        fields = {"fields": data}
        resp = requests.post(url, headers=headers, json=fields)
        
        if resp.status_code == 200:
            try:
                result = resp.json()
                if result.get('code') == 0:
                    return True
                else:
                    st.error(f"❌ Lỗi API: {result.get('msg', '')}")
            except Exception as e:
                st.error(f"❌ Lỗi parse response: {e}")
        else:
            st.error(f"❌ HTTP Error: {resp.status_code}")
    except Exception as e:
        st.error(f"❌ Lỗi khi ghi dữ liệu: {e}")
    
    return False

# --- UPDATE ---
def larkbase_update_data(app_token, table_id, record_id, data):
    token = larkbase_get_token()
    if not token:
        st.error("❌ Không xác thực được với Larkbase.")
        return False
    
    try:
        url = f"{API_HOST}/{app_token}/tables/{table_id}/records/{record_id}"
        resp = requests.put(url, headers=get_headers(token), json={"fields": data})
        
        if resp.status_code == 200:
            try:
                result = resp.json()
                if result.get('code') == 0:
                    return True
                else:
                    st.error(f"❌ Lỗi API: {result.get('msg', '')}")
            except Exception as e:
                st.error(f"❌ Lỗi parse response: {e}")
        else:
            st.error(f"❌ HTTP Error: {resp.status_code}")
    except Exception as e:
        st.error(f"❌ Lỗi khi cập nhật: {e}")
    
    return False

# --- DELETE ---
def larkbase_delete_record(app_token, table_id, record_id):
    token = larkbase_get_token()
    if not token:
        st.error("❌ Không xác thực được với Larkbase.")
        return False
    
    try:
        url = f"{API_HOST}/{app_token}/tables/{table_id}/records/{record_id}"
        resp = requests.delete(url, headers=get_headers(token))
        
        if resp.status_code == 200:
            try:
                result = resp.json()
                if result.get('code') == 0:
                    return True
                else:
                    st.error(f"❌ Lỗi API: {result.get('msg', '')}")
            except Exception as e:
                st.error(f"❌ Lỗi parse response: {e}")
        else:
            st.error(f"❌ HTTP Error: {resp.status_code}")
    except Exception as e:
        st.error(f"❌ Lỗi khi xóa: {e}")
    
    return False
