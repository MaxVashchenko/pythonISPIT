import csv
from pathlib import Path

from database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "export"


def sales_by_date(target_date) -> list[dict]:
    query = """
        SELECT s.id, s.sale_date, e.full_name AS employee, b.title AS book,
               s.actual_price, (s.actual_price - b.cost_price) AS profit
        FROM sales s
        JOIN employees e ON e.id = s.employee_id
        JOIN books b ON b.id = s.book_id
        WHERE s.sale_date = %s
        ORDER BY s.id;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (target_date,))
            return cur.fetchall()


def sales_by_period(date_from, date_to) -> list[dict]:
    query = """
        SELECT s.id, s.sale_date, e.full_name AS employee, b.title AS book,
               s.actual_price, (s.actual_price - b.cost_price) AS profit
        FROM sales s
        JOIN employees e ON e.id = s.employee_id
        JOIN books b ON b.id = s.book_id
        WHERE s.sale_date BETWEEN %s AND %s
        ORDER BY s.sale_date, s.id;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (date_from, date_to))
            return cur.fetchall()


def sales_by_employee(employee_id: int) -> list[dict]:
    query = """
        SELECT s.id, s.sale_date, e.full_name AS employee, b.title AS book,
               s.actual_price, (s.actual_price - b.cost_price) AS profit
        FROM sales s
        JOIN employees e ON e.id = s.employee_id
        JOIN books b ON b.id = s.book_id
        WHERE e.id = %s
        ORDER BY s.sale_date, s.id;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (employee_id,))
            return cur.fetchall()


def top_book(date_from, date_to) -> dict | None:
    query = """
        SELECT b.id, b.title, b.author, COUNT(*) AS sales_count
        FROM sales s
        JOIN books b ON b.id = s.book_id
        WHERE s.sale_date BETWEEN %s AND %s
        GROUP BY b.id, b.title, b.author
        ORDER BY sales_count DESC, b.title
        LIMIT 1;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (date_from, date_to))
            return cur.fetchone()


def top_employee(date_from, date_to) -> dict | None:
    """Найуспішніший продавець визначається за сумою прибутку."""
    query = """
        SELECT e.id, e.full_name,
               COUNT(*) AS sales_count,
               SUM(s.actual_price - b.cost_price) AS total_profit
        FROM sales s
        JOIN employees e ON e.id = s.employee_id
        JOIN books b ON b.id = s.book_id
        WHERE s.sale_date BETWEEN %s AND %s
        GROUP BY e.id, e.full_name
        ORDER BY total_profit DESC, sales_count DESC, e.full_name
        LIMIT 1;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (date_from, date_to))
            return cur.fetchone()


def total_profit(date_from, date_to) -> dict:
    query = """
        SELECT
            COUNT(*) AS sales_count,
            COALESCE(SUM(s.actual_price - b.cost_price), 0) AS total_profit
        FROM sales s
        JOIN books b ON b.id = s.book_id
        WHERE s.sale_date BETWEEN %s AND %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (date_from, date_to))
            return cur.fetchone()


def top_author(date_from, date_to) -> dict | None:
    query = """
        SELECT b.author, COUNT(*) AS sales_count
        FROM sales s
        JOIN books b ON b.id = s.book_id
        WHERE s.sale_date BETWEEN %s AND %s
        GROUP BY b.author
        ORDER BY sales_count DESC, b.author
        LIMIT 1;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (date_from, date_to))
            return cur.fetchone()


def top_genre(date_from, date_to) -> dict | None:
    query = """
        SELECT b.genre, COUNT(*) AS sales_count
        FROM sales s
        JOIN books b ON b.id = s.book_id
        WHERE s.sale_date BETWEEN %s AND %s
        GROUP BY b.genre
        ORDER BY sales_count DESC, b.genre
        LIMIT 1;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (date_from, date_to))
            return cur.fetchone()


def export_to_csv(rows: list[dict], filename: str) -> Path:
    if not rows:
        raise ValueError("Немає даних для експорту.")

    EXPORT_DIR.mkdir(exist_ok=True)
    if not filename.lower().endswith(".csv"):
        filename += ".csv"
    path = EXPORT_DIR / filename

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return path
