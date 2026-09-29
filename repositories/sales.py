from database import get_connection


SALE_SELECT = """
    SELECT
        s.id,
        s.employee_id,
        e.full_name AS employee,
        s.book_id,
        b.title AS book,
        b.author,
        s.sale_date,
        s.actual_price,
        b.cost_price,
        (s.actual_price - b.cost_price) AS profit
    FROM sales s
    JOIN employees e ON e.id = s.employee_id
    JOIN books b ON b.id = s.book_id
"""


def create_sale(employee_id: int, book_id: int, sale_date, actual_price) -> int:
    query = """
        INSERT INTO sales (employee_id, book_id, sale_date, actual_price)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (employee_id, book_id, sale_date, actual_price))
            return cur.fetchone()["id"]


def list_sales() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(SALE_SELECT + " ORDER BY s.id")
            return cur.fetchall()


def get_sale(sale_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(SALE_SELECT + " WHERE s.id = %s", (sale_id,))
            return cur.fetchone()


def update_sale(sale_id: int, employee_id: int, book_id: int, sale_date, actual_price) -> bool:
    query = """
        UPDATE sales
        SET employee_id = %s,
            book_id = %s,
            sale_date = %s,
            actual_price = %s
        WHERE id = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (employee_id, book_id, sale_date, actual_price, sale_id))
            return cur.rowcount > 0


def delete_sale(sale_id: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sales WHERE id = %s", (sale_id,))
            return cur.rowcount > 0
