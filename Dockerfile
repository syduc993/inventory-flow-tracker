# Sử dụng Python 3.10 làm base image
FROM python:3.10-slim

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép file requirements và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn
COPY . .

# Mở cổng 8000 cho Uvicorn
EXPOSE 8000

# Lệnh chạy ứng dụng với Uvicorn
# main:app -> file main.py, đối tượng app = FastAPI()
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
