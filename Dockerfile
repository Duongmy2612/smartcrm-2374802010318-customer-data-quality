# Ảnh của prototype L7 – Smart CRM (BT3, TD-35): một ảnh dùng cho pipeline (python -m src.pipeline), dashboard
# (streamlit) và bộ kiểm thử (pytest). Dựng và chạy: docs/deployment-guide.md – hai lệnh:
#     cp .env.example .env
#     docker compose up -d --build
# Ảnh KHÔNG chứa .env, dữ liệu thật hay báo cáo (xem .dockerignore); mật khẩu chỉ vào lúc chạy qua biến môi trường.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LANG=C.UTF-8

# Chạy bằng tài khoản thường (không phải root) – checklist bảo mật mục 3.
RUN useradd --create-home --uid 10001 app
WORKDIR /app

# Thư viện trước, mã nguồn sau: sửa mã không phải cài lại thư viện khi dựng lại ảnh.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Thư mục /app thuộc tài khoản app: pipeline ghi reports/, data/processed/; pytest ghi .pytest_cache/.
COPY --chown=app:app . .
RUN chown app:app /app
USER app

EXPOSE 8501
CMD ["python", "-m", "src.pipeline", "--tep", "data/mau/customers_mau.csv"]
