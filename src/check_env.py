import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

print("pandas:", pd.__version__)

# 1. Đọc dữ liệu mẫu
df = pd.DataFrame({
    "customer": ["A", "B", "C"],
    "revenue": [120, 80, 150]
})

print(df.describe())

# 2. Kiểm tra kết nối PostgreSQL
try:
    from sqlalchemy import create_engine, text

    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    with create_engine(url).connect() as conn:
        print("DB OK:", conn.execute(text("SELECT version()")).scalar())

except Exception as e:
    print("Chưa kết nối được CSDL:", e)
