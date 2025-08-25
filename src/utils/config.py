# src/utils/config.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ SỬA: Centralize tất cả tokens ở đây thay vì hardcode ở nhiều file
API_TOKENS = {
    # Main app token (dùng cho Larkbase operations)
    'MAIN_APP_TOKEN': os.getenv('MAIN_APP_TOKEN', 'Rm9PbvKLeaFFZcsSQpElnRjIgXg'),
    
    # API access token (dùng cho IMEX và Depot API)
    'NHANH_ACCESS_TOKEN': os.getenv('NHANH_ACCESS_TOKEN', 'twf9P1xFZCUUgwt8zR0XgNeB6V5jsbq2KHb14bxovqK1ppCxyADwOK8FzQlCEeEGABRZINXoUCSzM50kjhwcrUSBWTY5nSvyhfnH2X2cI0pC7pNczSVxc1ratdDmxF85q7hUTUNCrUnpPTG5ZwLNO7bkMlEEJTCdPhgYaC'),
    
    # App credentials for API calls
    'NHANH_APP_ID': os.getenv('NHANH_APP_ID', '74951'),
    'NHANH_BUSINESS_ID': os.getenv('NHANH_BUSINESS_ID', '8901'),
}

# ✅ SỬA: Table IDs centralization
TABLE_IDS = {
    'MAIN_TABLE_ID': os.getenv('MAIN_TABLE_ID', 'tblJJPUEFhsXHaxY'),
    'TRANSPORT_PROVIDERS_TABLE_ID': os.getenv('TRANSPORT_PROVIDERS_TABLE_ID', 'tblyiELQIi6M1j1r'),
}

# === AUTHENTICATION CONFIG ===
AUTH_CONFIG = {
    'LARK_APP_ID': os.getenv('LARK_APP_ID'),
    'LARK_APP_SECRET': os.getenv('LARK_APP_SECRET'), 
    'LARK_BASE_URL': os.getenv('LARK_BASE_URL', 'https://open.larksuite.com/open-apis'),
    'REDIRECT_URI': os.getenv('REDIRECT_URI', 'http://localhost:8000/auth/callback'),
    # ✅ SỬA: Sử dụng centralized token thay vì duplicate
    'AUTH_APP_TOKEN': API_TOKENS['MAIN_APP_TOKEN'], 
    'AUTH_TABLE_ID': os.getenv('AUTH_TABLE_ID', 'tblPermissions'),
    'SECRET_KEY': os.getenv('SECRET_KEY', 'your-super-secret-key-change-this-in-production'),
    'SESSION_EXPIRE_HOURS': int(os.getenv('SESSION_EXPIRE_HOURS', '24'))
}

# ============================================================================
# ===  FORM FIELD CONFIGURATIONS  ===
# ============================================================================

# Danh sách cột hiển thị trong form (theo thứ tự mong muốn)
LARKBASE_FIELDS = [
    "ID",
    "ID kho đi",
    "Kho đi", 
    "ID kho đến",
    "Kho đến",
    "Số lượng bao",
    "Số lượng bao/tải giao", 
    "ID người bàn giao",
    "Người bàn giao",
    "Ngày bàn giao",
    "Đơn vị vận chuyển",
    "Số lượng bao tải nhận",
    "Người nhận", 
    "Ngày nhận hàng",
    "Thiếu thừa bao"
]

# === QUY TẮC NHẬP LIỆU ===

# Các trường người dùng có thể nhập liệu khi TẠO MỚI bản ghi.
CREATABLE_FIELDS = [
    "Số lượng bao/tải giao",
    "Người bàn giao",
    "Đơn vị vận chuyển"
]

# Các trường người dùng có thể nhập liệu khi CẬP NHẬT bản ghi.
UPDATABLE_FIELDS = [
    "Số lượng bao/tải giao",
    "Người bàn giao",
    "Đơn vị vận chuyển"
]

# Các trường khi đã có dữ liệu sẽ:
# 1. Tự khóa chính nó, không cho sửa nữa.
# 2. Khóa không cho xóa toàn bộ bản ghi.
LOCK_FIELDS = [
    "Số lượng bao tải nhận",
    "Người nhận",
    "Ngày nhận hàng"
]

# === DỮ LIỆU NỀN ===

# Các cột lấy từ API (không hiển thị trong form nhưng vẫn lưu vào database)
API_FIELDS = [
    "ID kho đi", "Kho đi", "ID kho đến", "Kho đến", "Số lượng", 
    "Số lượng sản phẩm yêu cầu", "Số lượng sản phẩm hỏng", 
    "Số lượng sản phẩm yêu cầu được duyệt", "Số lượng sản phẩm yêu cầu được xác nhận", 
    "Ngày tạo", "Ngày duyệt", "Ngày xác nhận", "Người xác nhận"
]

# Toàn bộ fields để lưu vào Larkbase (hiện không dùng trong app.py)
ALL_LARKBASE_FIELDS = LARKBASE_FIELDS + API_FIELDS

# ============================================================================
# ===  VALIDATION & HELPER FUNCTIONS  ===
# ============================================================================

# Validate required auth config
REQUIRED_AUTH_VARS = ['LARK_APP_ID', 'LARK_APP_SECRET']
for var in REQUIRED_AUTH_VARS:
    if not AUTH_CONFIG[var]:
        raise ValueError(f"Missing required environment variable: {var}")

# ✅ SỬA: Helper functions để get tokens safely
def get_main_app_token():
    """Lấy main app token cho Larkbase operations"""
    return API_TOKENS['MAIN_APP_TOKEN']

def get_nhanh_access_token():
    """Lấy access token cho Nhanh API calls"""
    return API_TOKENS['NHANH_ACCESS_TOKEN']

def get_nhanh_credentials():
    """Lấy đầy đủ credentials cho Nhanh API"""
    return {
        'app_id': API_TOKENS['NHANH_APP_ID'],
        'business_id': API_TOKENS['NHANH_BUSINESS_ID'],
        'access_token': API_TOKENS['NHANH_ACCESS_TOKEN']
    }

def get_table_id(table_name='main'):
    """Lấy table ID theo tên"""
    table_map = {
        'main': TABLE_IDS['MAIN_TABLE_ID'],
        'transport': TABLE_IDS['TRANSPORT_PROVIDERS_TABLE_ID']
    }
    return table_map.get(table_name, TABLE_IDS['MAIN_TABLE_ID'])
