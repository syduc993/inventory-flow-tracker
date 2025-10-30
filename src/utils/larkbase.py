# FILE: src/utils/larkbase.py (ĐÃ SỬA LỖI UnboundLocalError)

import requests
import logging
import os
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

logging.basicConfig(level=logging.INFO)
API_ENDPOINT = 'https://open.larksuite.com/open-apis'
API_HOST = "https://open.larksuite.com/open-apis/bitable/v1/apps"

LARK_APP_ID = os.getenv('LARK_APP_ID', 'cli_a7fab27260385010')
LARK_APP_SECRET = os.getenv('LARK_APP_SECRET', 'Zg4MVcFfiOu0g09voTcpfd4WGDpA0Ly5')

try:
    client = lark.Client.builder() \
        .app_id(LARK_APP_ID) \
        .app_secret(LARK_APP_SECRET) \
        .log_level(lark.LogLevel.INFO) \
        .build()
    logging.info("✅ Khởi tạo Lark SDK client thành công.")
except Exception as e:
    client = None
    logging.error(f"❌ Lỗi khi khởi tạo Lark SDK client: {e}")

def larkbase_get_token(app_id=None, app_secret=None, endpoint=API_ENDPOINT):
    APP_ID = app_id or LARK_APP_ID
    APP_SECRET = app_secret or LARK_APP_SECRET
    url = f"{endpoint}/auth/v3/tenant_access_token/internal"
    try:
        resp = requests.post(url, json={'app_id': APP_ID, 'app_secret': APP_SECRET})
        if resp.status_code == 200 and resp.json().get('code') == 0:
            return resp.json()['tenant_access_token']
    except Exception as e:
        logging.error(f"Lỗi khi lấy token: {e}")
    return None

def get_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
def larkbase_get_all(app_token, table_id):
    token = larkbase_get_token()
    if not token:
        logging.error("Không xác thực được với Larkbase.")
        return []
    all_records, page_token = [], ""
    while True:
        try:
            url = f"{API_HOST}/{app_token}/tables/{table_id}/records?page_size=500"
            if page_token: url += f"&page_token={page_token}"
            
            resp = requests.get(url, headers=get_headers(token))
            if resp.status_code != 200: break
            
            res_data = resp.json()
            if res_data.get("code") != 0: break
            data = res_data.get("data")
            if not data or not data.get("items"): break
            all_records.extend(data["items"])
            page_token = data.get("page_token", "")
            if not page_token: break
        except Exception as e:
            logging.error(f"Lỗi khi lấy dữ liệu: {e}"); break
    return all_records

def larkbase_find_by_field(app_token, table_id, field, value):
    all_records = larkbase_get_all(app_token, table_id)
    if not all_records:
        return False, None
    for record in all_records:
        fields = record.get('fields', {})
        field_value = fields.get(field)

        if isinstance(field_value, list) and field_value:
            first_item = field_value[0]
            if isinstance(first_item, dict) and 'text' in first_item:
                value_to_compare = first_item.get('text', '')
            else:
                value_to_compare = str(field_value)
        else:
            value_to_compare = field_value

        if str(value_to_compare or '').strip() == str(value or '').strip():
            return True, record
            
    return False, None

def larkbase_write_data(app_token, table_id, data):
    token = larkbase_get_token()
    if not token: return False, "Không thể xác thực với Larkbase."
    try:
        url = f"{API_HOST}/{app_token}/tables/{table_id}/records"
        resp = requests.post(url, headers=get_headers(token), json={"fields": data})
        res_json = resp.json()
        if resp.status_code == 200 and res_json.get('code') == 0:
            return True, "Thêm mới thành công"
        return False, res_json.get('msg', resp.text)
    except Exception as e: return False, str(e)

def larkbase_update_data(app_token, table_id, record_id, data):
    token = larkbase_get_token()
    if not token: return False, "Không thể xác thực với Larkbase."
    try:
        url = f"{API_HOST}/{app_token}/tables/{table_id}/records/{record_id}"
        resp = requests.put(url, headers=get_headers(token), json={"fields": data})
        res_json = resp.json()
        if resp.status_code == 200 and res_json.get('code') == 0:
            return True, "Cập nhật thành công"
        return False, res_json.get('msg', resp.text)
    except Exception as e: return False, str(e)

def larkbase_delete_record(app_token, table_id, record_id):
    token = larkbase_get_token()
    if not token: return False, "Không thể xác thực với Larkbase."
    try:
        url = f"{API_HOST}/{app_token}/tables/{table_id}/records/{record_id}"
        resp = requests.delete(url, headers=get_headers(token))
        res_json = resp.json()
        if resp.status_code == 200 and res_json.get('code') == 0:
            return True, "Xóa thành công"
        return False, res_json.get('msg', resp.text)
    except Exception as e: return False, str(e)
        
def larkbase_batch_write_data(app_token, table_id, records_data):
    token = larkbase_get_token()
    if not token: return False, "Không thể xác thực với Larkbase."
    try:
        url = f"{API_HOST}/{app_token}/tables/{table_id}/records/batch_create"
        records = [{"fields": record} for record in records_data]
        resp = requests.post(url, headers=get_headers(token), json={"records": records})
        res_json = resp.json()
        if resp.status_code == 200 and res_json.get('code') == 0:
            created_count = len(res_json.get('data', {}).get('records', []))
            return True, f"Thêm thành công {created_count} bản ghi"
        return False, res_json.get('msg', resp.text)
    except Exception as e: return False, str(e)

def larkbase_search_records(app_token, table_id, filter_conditions=None, page_size=500):
    if not client:
        logging.error("Lark SDK client chưa được khởi tạo.")
        return []
    all_records_as_dicts, page_token, page_count = [], None, 0
    sdk_conditions = []
    if filter_conditions:
        for cond in filter_conditions:
            sdk_conditions.append(Condition.builder().field_name(cond.get('field_name')).operator(cond.get('operator')).value(cond.get('value')).build())
    logging.info(f"Bắt đầu tìm kiếm SDK với {len(sdk_conditions)} điều kiện.")
    while page_count < 20:
        page_count += 1
        try:
            request_builder = SearchAppTableRecordRequest.builder().app_token(app_token).table_id(table_id).page_size(page_size)
            if page_token: request_builder.page_token(page_token)
            request_body_builder = SearchAppTableRecordRequestBody.builder()
            if sdk_conditions:
                request_body_builder.filter(FilterInfo.builder().conjunction("and").conditions(sdk_conditions).build())
            request = request_builder.request_body(request_body_builder.build()).build()
            response = client.bitable.v1.app_table_record.search(request)
            if not response.success():
                logging.error(f"Lỗi khi gọi SDK (trang {page_count}): {response.code} - {response.msg}"); break
            
            # ✅ SỬA LỖI: Tách thành 2 dòng riêng biệt
            data = response.data
            items = data.items or []

            if not items: break
            for item in items: all_records_as_dicts.append({'record_id': item.record_id, 'fields': item.fields})
            if not data.has_more: break
            page_token = data.page_token
        except Exception as e:
            logging.error(f"Lỗi ngoại lệ trong quá trình tìm kiếm với SDK: {e}", exc_info=True); break
    logging.info(f"✅ Hoàn tất tìm kiếm SDK. Tổng cộng {len(all_records_as_dicts)} bản ghi.")
    return all_records_as_dicts