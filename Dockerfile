# Sử dụng một image Python chính thức, gọn nhẹ
FROM python:3.9-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Cài đặt các biến môi trường cần thiết cho Streamlit
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8080

# Sao chép file requirements trước để tận dụng cache của Docker
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn còn lại của ứng dụng
COPY . .

# Mở cổng 8080 để container có thể nhận kết nối từ bên ngoài
EXPOSE 8080

# Lệnh để khởi chạy ứng dụng Streamlit
# Streamlit sẽ tự động sử dụng các biến môi trường đã cài đặt ở trên
CMD ["streamlit", "run", "app.py"]
