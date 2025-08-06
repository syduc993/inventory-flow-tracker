# Sử dụng Python base
FROM python:3.10-slim

# Cài đặt các gói cần thiết cho hệ điều hành
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy code và requirements
COPY requirements.txt .


# Tạo thư mục src để copy code theo cấu trúc
RUN mkdir -p src/styles src/utils

# Copy toàn bộ code vào trong workdir
COPY ./src ./src
COPY app.py ./

# Cài đặt các package pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
