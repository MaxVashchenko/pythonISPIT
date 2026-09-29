from database import get_connection


def create_book(isbn: str, title: str, publication_year: int, author: str, genre: str, cost_price, potential_sale_price) -> int:
    query = """
        INSERT INTO books (
            isbn, title, publication_year, author, genre, cost_price, potential_sale_price
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (isbn, title, publication_year, author, genre, cost_price, potential_sale_price),
            )
            return cur.fetchone()["id"]


def list_books() -> list[dict]:
    query = """
        SELECT id, isbn, title, publication_year, author, genre,
               cost_price, potential_sale_price
        FROM books
        ORDER BY id;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


def get_book(book_id: int) -> dict | None:
    query = """
        SELECT id, isbn, title, publication_year, author, genre,
               cost_price, potential_sale_price
        FROM books
        WHERE id = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (book_id,))
            return cur.fetchone()


def update_book(book_id: int, isbn: str, title: str, publication_year: int, author: str, genre: str, cost_price, potential_sale_price) -> bool:
    query = """
        UPDATE books
        SET isbn = %s,
            title = %s,
            publication_year = %s,
            author = %s,
            genre = %s,
            cost_price = %s,
            potential_sale_price = %s
        WHERE id = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (isbn, title, publication_year, author, genre, cost_price, potential_sale_price, book_id),
            )
            return cur.rowcount > 0


def delete_book(book_id: int) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
            return cur.rowcount > 0


def is_unique_isbn(isbn: str, exclude_id: int | None = None) -> bool:
    query = "SELECT 1 FROM books WHERE isbn = %s"
    params: list = [isbn]
    if exclude_id is not None:
        query += " AND id <> %s"
        params.append(exclude_id)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone() is None
