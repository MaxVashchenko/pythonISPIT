INSERT INTO employees (full_name, position, phone, email)
VALUES
    ('Іван Петренко', 'Продавець', '+380671112233', 'ivan.petrenko@example.com'),
    ('Олена Коваль', 'Старший продавець', '+380931234567', 'olena.koval@example.com'),
    ('Марія Бондар', 'Продавець', '+380501234567', 'maria.bondar@example.com')
ON CONFLICT (email) DO NOTHING;

INSERT INTO books (isbn, title, publication_year, author, genre, cost_price, potential_sale_price)
VALUES
    ('9786176798919', 'Python для початківців', 2024, 'Олександр Савчук', 'Програмування', 320.00, 499.00),
    ('9786171700504', 'Чистий код', 2023, 'Роберт Мартін', 'Програмування', 450.00, 690.00),
    ('9789669829626', '1984', 2022, 'Джордж Орвелл', 'Антиутопія', 180.00, 299.00),
    ('9786171701235', 'Маленький принц', 2021, 'Антуан де Сент-Екзюпері', 'Художня література', 120.00, 220.00),
    ('9786176797301', 'Алгоритми', 2024, 'Томас Кормен', 'Програмування', 700.00, 990.00)
ON CONFLICT (isbn) DO NOTHING;

INSERT INTO sales (employee_id, book_id, sale_date, actual_price)
SELECT e.id, b.id, CURRENT_DATE - 5, 480.00
FROM employees e, books b
WHERE e.email = 'ivan.petrenko@example.com' AND b.isbn = '9786176798919'
  AND NOT EXISTS (
      SELECT 1 FROM sales s
      WHERE s.employee_id = e.id AND s.book_id = b.id
        AND s.sale_date = CURRENT_DATE - 5 AND s.actual_price = 480.00
  );

INSERT INTO sales (employee_id, book_id, sale_date, actual_price)
SELECT e.id, b.id, CURRENT_DATE - 3, 650.00
FROM employees e, books b
WHERE e.email = 'olena.koval@example.com' AND b.isbn = '9786171700504'
  AND NOT EXISTS (
      SELECT 1 FROM sales s
      WHERE s.employee_id = e.id AND s.book_id = b.id
        AND s.sale_date = CURRENT_DATE - 3 AND s.actual_price = 650.00
  );

INSERT INTO sales (employee_id, book_id, sale_date, actual_price)
SELECT e.id, b.id, CURRENT_DATE - 2, 290.00
FROM employees e, books b
WHERE e.email = 'maria.bondar@example.com' AND b.isbn = '9789669829626'
  AND NOT EXISTS (
      SELECT 1 FROM sales s
      WHERE s.employee_id = e.id AND s.book_id = b.id
        AND s.sale_date = CURRENT_DATE - 2 AND s.actual_price = 290.00
  );

INSERT INTO sales (employee_id, book_id, sale_date, actual_price)
SELECT e.id, b.id, CURRENT_DATE - 1, 470.00
FROM employees e, books b
WHERE e.email = 'olena.koval@example.com' AND b.isbn = '9786176798919'
  AND NOT EXISTS (
      SELECT 1 FROM sales s
      WHERE s.employee_id = e.id AND s.book_id = b.id
        AND s.sale_date = CURRENT_DATE - 1 AND s.actual_price = 470.00
  );
