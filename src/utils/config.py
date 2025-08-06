# src/utils/config.py

# Danh sách cột hiển thị trong form (theo thứ tự mong muốn)
LARKBASE_FIELDS = [
    "ID",
    "Số lượng bao/tải giao", 
    "Người bàn giao",
    "Ngày bàn giao",
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
]

# Các trường người dùng có thể nhập liệu khi CẬP NHẬT bản ghi.
UPDATABLE_FIELDS = [
    "Số lượng bao/tải giao",
    "Người bàn giao"
]

# Các trường khi đã có dữ liệu sẽ:
# 1. Tự khóa chính nó, không cho sửa nữa.
# 2. Khóa không cho xóa toàn bộ bản ghi.
# *** FIX: Thêm "Thiếu thừa bao" vào danh sách khóa ***
LOCK_FIELDS = [
    "Số lượng bao tải nhận",
    "Người nhận",
    "Ngày nhận hàng"
]

# === DỮ LIỆU NỀN ===

# Các cột lấy từ API (không hiển thị trong form nhưng vẫn lưu vào database)
API_FIELDS = [
    "Kho đi", "Kho đến", "Số lượng", "Số lượng sản phẩm yêu cầu",
    "Số lượng sản phẩm hỏng", "Số lượng sản phẩm yêu cầu được duyệt",
    "Số lượng sản phẩm yêu cầu được xác nhận", "Ngày tạo", "Ngày duyệt", 
    "Ngày xác nhận", "Người xác nhận"
]

# Toàn bộ fields để lưu vào Larkbase (hiện không dùng trong app.py)
ALL_LARKBASE_FIELDS = LARKBASE_FIELDS + API_FIELDS
