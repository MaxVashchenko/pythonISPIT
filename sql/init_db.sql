CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    position VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    publication_year INTEGER NOT NULL CHECK (publication_year BETWEEN 1000 AND 2100),
    author VARCHAR(150) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    cost_price NUMERIC(12, 2) NOT NULL CHECK (cost_price > 0),
    potential_sale_price NUMERIC(12, 2) NOT NULL CHECK (potential_sale_price > 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    actual_price NUMERIC(12, 2) NOT NULL CHECK (actual_price > 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sales_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_sales_book
        FOREIGN KEY (book_id)
        REFERENCES books(id)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_employee ON sales(employee_id);
CREATE INDEX IF NOT EXISTS idx_sales_book ON sales(book_id);
