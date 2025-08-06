# Sử dụng một image Python chính thức, gọn nhẹ
FROM python:3.9-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Sao chép file requirements trước để tận dụng cache của Docker
COPY requirements.txt .

# Cài đặt các thư viện Python
# Đảm bảo requirements.txt có đủ thư viện!
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn còn lại của ứng dụng
COPY . .

# Mở cổng 8080 (chủ yếu mang tính thông báo cho người đọc Dockerfile)
# Cloud Run sẽ tự động quản lý cổng này
EXPOSE 8080

# Lệnh để khởi chạy ứng dụng Streamlit
# Quan trọng: Lắng nghe trên cổng do biến $PORT cung cấp, và địa chỉ 0.0.0.0
# Cách này linh hoạt hơn là dùng ENV để gán cứng cổng.
CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0
