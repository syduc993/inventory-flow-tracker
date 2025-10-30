# FILE: test_larkbase_data.py (Nâng cấp để kiểm tra nhiều cột)
import os
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
import logging
from dotenv import load_dotenv

# --- CẤU HÌNH ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv() # Tải các biến từ file .env

# Lấy thông tin từ biến môi trường
LARK_APP_ID = os.getenv('LARK_APP_ID')
LARK_APP_SECRET = os.getenv('LARK_APP_SECRET')
APP_TOKEN = os.getenv('MAIN_APP_TOKEN')
TABLE_ID = os.getenv('MAIN_TABLE_ID')

# ==============================================================================
# ✅ THAY ĐỔI CHÍNH: CHỈ CẦN SỬA DANH SÁCH DƯỚI ĐÂY ĐỂ KIỂM TRA CÁC CỘT BẠN MUỐN
# ==============================================================================
FIELDS_TO_INSPECT = [
    "ID",
    "Kho đi",               # Cột có khả năng gây lỗi
    "Kho đến",              # Cột có khả năng gây lỗi
    "Đơn vị vận chuyển",    # Cột đã được sửa
    "Người bàn giao",       # Cột Person
    "Số lượng bao",         # Cột Number
    "Ngày bàn giao",        # Cột Date/Timestamp
    "Group ID"              # Cột Text
]
# ==============================================================================

def inspect_larkbase_fields():
    """
    Kết nối đến Larkbase, lấy một vài bản ghi và in ra giá trị cũng như
    kiểu dữ liệu của TẤT CẢ các cột được định nghĩa trong FIELDS_TO_INSPECT.
    """
    if not all([LARK_APP_ID, LARK_APP_SECRET, APP_TOKEN, TABLE_ID]):
        logging.error("Lỗi: Vui lòng kiểm tra lại các biến môi trường trong file .env")
        return

    # Khởi tạo Lark SDK client
    try:
        client = lark.Client.builder() \
            .app_id(LARK_APP_ID) \
            .app_secret(LARK_APP_SECRET) \
            .log_level(lark.LogLevel.ERROR) \
            .build()
    except Exception as e:
        logging.error(f"Lỗi khi khởi tạo Lark SDK client: {e}")
        return

    logging.info(f"Đang tiến hành lấy 5 bản ghi từ bảng ID: {TABLE_ID}...")

    try:
        request_body = SearchAppTableRecordRequestBody.builder().build()
        request = SearchAppTableRecordRequest.builder() \
            .app_token(APP_TOKEN) \
            .table_id(TABLE_ID) \
            .page_size(5) \
            .request_body(request_body) \
            .build()

        response = client.bitable.v1.app_table_record.search(request)

        if not response.success():
            logging.error(f"Lỗi API: {response.code} - {response.msg}")
            return

        items = response.data.items or []
        if not items:
            logging.warning("Không tìm thấy bản ghi nào để kiểm tra.")
            return

        # ✅ THAY ĐỔI: In kết quả cho nhiều cột
        print("\n" + "="*80)
        print(f"KẾT QUẢ KIỂM TRA CÁC CỘT: {', '.join(FIELDS_TO_INSPECT)}")
        print("="*80)

        # Duyệt qua từng bản ghi
        for i, item in enumerate(items):
            fields = item.fields
            record_id = item.record_id

            print(f"\n[Bản ghi #{i+1}] - Record ID: {record_id}")
            
            # ✅ THAY ĐỔI: Duyệt qua từng cột trong danh sách cần kiểm tra
            for field_name in FIELDS_TO_INSPECT:
                field_value = fields.get(field_name) # Dùng .get() để tránh lỗi nếu cột không tồn tại

                print(f"  --- Cột: '{field_name}' ---")
                print(f"      - Giá trị: {field_value}")
                print(f"      - Kiểu dữ liệu: {type(field_value)}")
        
        print("\n" + "="*80)
        logging.info("Kiểm tra hoàn tất.")

    except Exception as e:
        logging.error(f"Lỗi ngoại lệ trong quá trình kiểm tra: {e}", exc_info=True)


if __name__ == "__main__":
    inspect_larkbase_fields()