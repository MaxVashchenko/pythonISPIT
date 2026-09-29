from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from config import DB_CONFIG

BASE_DIR = Path(__file__).resolve().parent


def get_connection():
    """Повертає нове з'єднання з PostgreSQL."""
    return psycopg.connect(**DB_CONFIG, row_factory=dict_row)


def run_sql_file(path: str | Path) -> None:
    """Виконує SQL-файл у транзакції."""
    sql_path = Path(path)
    sql = sql_path.read_text(encoding="utf-8")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def init_db() -> None:
    run_sql_file(BASE_DIR / "sql" / "init_db.sql")


def seed_db() -> None:
    run_sql_file(BASE_DIR / "sql" / "seed.sql")


def check_connection() -> bool:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS ok")
                return cur.fetchone()["ok"] == 1
    except Exception:
        return False
