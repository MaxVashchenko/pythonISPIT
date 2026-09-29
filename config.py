import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "book_sales"),
    "user": os.getenv("DB_USER", "postgres"),
}

# Порожній DB_HOST означає локальний Unix socket PostgreSQL.
host = os.getenv("DB_HOST", "localhost").strip()
password = os.getenv("DB_PASSWORD", "")

if host:
    DB_CONFIG["host"] = host

if password:
    DB_CONFIG["password"] = password
