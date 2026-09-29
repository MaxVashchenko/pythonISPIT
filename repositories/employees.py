from psycopg import errors

from database import get_connection


def create_employee(full_name: str, position: str, phone: str, email: str) -> int:
    query = """
        INSERT INTO employees (full_name, position, phone, email)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (full_name, position, phone, email))
            return cur.fetchone()["id"]


def list_employees() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, full_name, position, phone, email FROM employees ORDER BY id")
            return cur.fetchall()


def get_employee(employee_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, full_name, position, phone, email FROM employees WHERE id = %s",
                (employee_id,),
            )
            return cur.fetchone()


def update_employee(employee_id: int, full_name: str, position: str, phone: str, email: str) -> bool:
    query = """
        UPDATE employees
        SET full_name = %s, position = %s, phone = %s, email = %s
        WHERE id = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (full_name, position, phone, email, employee_id))
            return cur.rowcount > 0


def delete_employee(employee_id: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
            return cur.rowcount > 0


def is_unique_email(email: str, exclude_id: int | None = None) -> bool:
    query = "SELECT 1 FROM employees WHERE email = %s"
    params: list = [email]
    if exclude_id is not None:
        query += " AND id <> %s"
        params.append(exclude_id)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone() is None


IntegrityError = errors.UniqueViolation
