from datetime import date
from decimal import Decimal

from psycopg import errors

from repositories import books, employees, sales
from services import reports
from utils.formatters import money, print_rows
from utils.input_helpers import (
    confirm,
    optional_date,
    optional_decimal,
    optional_email,
    optional_int,
    optional_isbn,
    optional_phone,
    optional_text,
    read_date,
    read_email,
    read_int,
    read_isbn,
    read_non_empty,
    read_phone,
    read_positive_decimal,
)


def pause() -> None:
    input("\nНатисніть Enter, щоб продовжити...")


def print_employee(employee: dict) -> None:
    print(f"ID: {employee['id']}")
    print(f"ПІБ: {employee['full_name']}")
    print(f"Посада: {employee['position']}")
    print(f"Телефон: {employee['phone']}")
    print(f"Email: {employee['email']}")


def print_book(book: dict) -> None:
    print(f"ID: {book['id']}")
    print(f"ISBN: {book['isbn']}")
    print(f"Назва: {book['title']}")
    print(f"Рік: {book['publication_year']}")
    print(f"Автор: {book['author']}")
    print(f"Жанр: {book['genre']}")
    print(f"Собівартість: {money(book['cost_price'])}")
    print(f"Потенційна ціна продажу: {money(book['potential_sale_price'])}")


def print_sale(sale: dict) -> None:
    print(f"ID: {sale['id']}")
    print(f"Дата: {sale['sale_date']}")
    print(f"Співробітник: {sale['employee']} (ID {sale['employee_id']})")
    print(f"Книга: {sale['book']} (ID {sale['book_id']})")
    print(f"Ціна продажу: {money(sale['actual_price'])}")
    print(f"Собівартість: {money(sale['cost_price'])}")
    print(f"Прибуток: {money(sale['profit'])}")


def employees_menu() -> None:
    while True:
        print("\n=== СПІВРОБІТНИКИ ===")
        print("1. Додати")
        print("2. Показати список")
        print("3. Переглянути деталі")
        print("4. Редагувати")
        print("5. Видалити")
        print("0. Назад")

        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            full_name = read_non_empty("ПІБ: ")
            position = read_non_empty("Посада: ")
            phone = read_phone("Телефон: ")
            email = read_email("Email: ")

            if not employees.is_unique_email(email):
                print("Співробітник з таким email вже існує.")
                pause()
                continue

            employee_id = employees.create_employee(full_name, position, phone, email)
            print(f"Співробітника створено. ID = {employee_id}")
            pause()

        elif choice == "2":
            rows = employees.list_employees()
            print_rows(rows, [
                ("id", "ID"),
                ("full_name", "ПІБ"),
                ("position", "Посада"),
                ("phone", "Телефон"),
                ("email", "Email"),
            ])
            pause()

        elif choice == "3":
            employee_id = read_int("ID співробітника: ", 1)
            employee = employees.get_employee(employee_id)
            if employee:
                print_employee(employee)
            else:
                print("Співробітника не знайдено.")
            pause()

        elif choice == "4":
            employee_id = read_int("ID співробітника: ", 1)
            employee = employees.get_employee(employee_id)
            if not employee:
                print("Співробітника не знайдено.")
                pause()
                continue

            full_name = optional_text("ПІБ", employee["full_name"])
            position = optional_text("Посада", employee["position"])
            phone = optional_phone("Телефон", employee["phone"])
            email = optional_email("Email", employee["email"])

            if not employees.is_unique_email(email, exclude_id=employee_id):
                print("Такий email вже використовується.")
                pause()
                continue

            employees.update_employee(employee_id, full_name, position, phone, email)
            print("Дані співробітника оновлено.")
            pause()

        elif choice == "5":
            employee_id = read_int("ID співробітника: ", 1)
            employee = employees.get_employee(employee_id)
            if not employee:
                print("Співробітника не знайдено.")
                pause()
                continue

            print_employee(employee)
            if not confirm("Видалити співробітника? [y/n]: "):
                continue

            try:
                employees.delete_employee(employee_id)
                print("Співробітника видалено.")
            except errors.ForeignKeyViolation:
                print("Неможливо видалити: співробітник має пов'язані продажі.")
            pause()

        elif choice == "0":
            return
        else:
            print("Невідомий пункт меню.")


def books_menu() -> None:
    while True:
        print("\n=== КНИГИ ===")
        print("1. Додати")
        print("2. Показати список")
        print("3. Переглянути деталі")
        print("4. Редагувати")
        print("5. Видалити")
        print("0. Назад")

        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            isbn = read_isbn("ISBN: ")
            if not books.is_unique_isbn(isbn):
                print("Книга з таким ISBN вже існує.")
                pause()
                continue

            title = read_non_empty("Назва: ")
            publication_year = read_int("Рік публікації: ", 1000, date.today().year + 1)
            author = read_non_empty("Автор: ")
            genre = read_non_empty("Жанр: ")
            cost_price = read_positive_decimal("Собівартість: ")
            potential_sale_price = read_positive_decimal("Потенційна ціна продажу: ")

            book_id = books.create_book(
                isbn, title, publication_year, author, genre, cost_price, potential_sale_price
            )
            print(f"Книгу створено. ID = {book_id}")
            pause()

        elif choice == "2":
            rows = books.list_books()
            print_rows(rows, [
                ("id", "ID"),
                ("isbn", "ISBN"),
                ("title", "Назва"),
                ("publication_year", "Рік"),
                ("author", "Автор"),
                ("genre", "Жанр"),
                ("cost_price", "Собівартість"),
                ("potential_sale_price", "Ціна продажу"),
            ])
            pause()

        elif choice == "3":
            book_id = read_int("ID книги: ", 1)
            book = books.get_book(book_id)
            if book:
                print_book(book)
            else:
                print("Книгу не знайдено.")
            pause()

        elif choice == "4":
            book_id = read_int("ID книги: ", 1)
            book = books.get_book(book_id)
            if not book:
                print("Книгу не знайдено.")
                pause()
                continue

            isbn = optional_isbn("ISBN", book["isbn"])
            if not books.is_unique_isbn(isbn, exclude_id=book_id):
                print("Такий ISBN вже використовується.")
                pause()
                continue

            title = optional_text("Назва", book["title"])
            publication_year = optional_int(
                "Рік публікації", book["publication_year"], 1000, date.today().year + 1
            )
            author = optional_text("Автор", book["author"])
            genre = optional_text("Жанр", book["genre"])
            cost_price = optional_decimal("Собівартість", book["cost_price"])
            potential_sale_price = optional_decimal(
                "Потенційна ціна продажу", book["potential_sale_price"]
            )

            books.update_book(
                book_id, isbn, title, publication_year, author, genre, cost_price, potential_sale_price
            )
            print("Дані книги оновлено.")
            pause()

        elif choice == "5":
            book_id = read_int("ID книги: ", 1)
            book = books.get_book(book_id)
            if not book:
                print("Книгу не знайдено.")
                pause()
                continue

            print_book(book)
            if not confirm("Видалити книгу? [y/n]: "):
                continue

            try:
                books.delete_book(book_id)
                print("Книгу видалено.")
            except errors.ForeignKeyViolation:
                print("Неможливо видалити: книга має пов'язані продажі.")
            pause()

        elif choice == "0":
            return
        else:
            print("Невідомий пункт меню.")


def sales_menu() -> None:
    while True:
        print("\n=== ПРОДАЖІ ===")
        print("1. Додати продаж")
        print("2. Показати список")
        print("3. Переглянути деталі")
        print("4. Редагувати")
        print("5. Видалити")
        print("0. Назад")

        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            employee_id = read_int("ID співробітника: ", 1)
            if not employees.get_employee(employee_id):
                print("Співробітника з таким ID не існує.")
                pause()
                continue

            book_id = read_int("ID книги: ", 1)
            if not books.get_book(book_id):
                print("Книги з таким ID не існує.")
                pause()
                continue

            sale_date = read_date("Дата продажу (YYYY-MM-DD): ")
            actual_price = read_positive_decimal("Реальна ціна продажу: ")

            sale_id = sales.create_sale(employee_id, book_id, sale_date, actual_price)
            print(f"Продаж створено. ID = {sale_id}")
            sale = sales.get_sale(sale_id)
            print(f"Прибуток з продажу: {money(sale['profit'])}")
            pause()

        elif choice == "2":
            rows = sales.list_sales()
            print_rows(rows, [
                ("id", "ID"),
                ("sale_date", "Дата"),
                ("employee", "Співробітник"),
                ("book", "Книга"),
                ("actual_price", "Продаж"),
                ("profit", "Прибуток"),
            ])
            pause()

        elif choice == "3":
            sale_id = read_int("ID продажу: ", 1)
            sale = sales.get_sale(sale_id)
            if sale:
                print_sale(sale)
            else:
                print("Продаж не знайдено.")
            pause()

        elif choice == "4":
            sale_id = read_int("ID продажу: ", 1)
            sale = sales.get_sale(sale_id)
            if not sale:
                print("Продаж не знайдено.")
                pause()
                continue

            employee_id = optional_int("ID співробітника", sale["employee_id"], 1)
            if not employees.get_employee(employee_id):
                print("Співробітника з таким ID не існує.")
                pause()
                continue

            book_id = optional_int("ID книги", sale["book_id"], 1)
            if not books.get_book(book_id):
                print("Книги з таким ID не існує.")
                pause()
                continue

            sale_date = optional_date("Дата продажу", sale["sale_date"])
            actual_price = optional_decimal("Реальна ціна", sale["actual_price"])

            sales.update_sale(sale_id, employee_id, book_id, sale_date, actual_price)
            print("Продаж оновлено.")
            pause()

        elif choice == "5":
            sale_id = read_int("ID продажу: ", 1)
            sale = sales.get_sale(sale_id)
            if not sale:
                print("Продаж не знайдено.")
                pause()
                continue

            print_sale(sale)
            if confirm("Видалити продаж? [y/n]: "):
                sales.delete_sale(sale_id)
                print("Продаж видалено.")
            pause()

        elif choice == "0":
            return
        else:
            print("Невідомий пункт меню.")


def _period():
    date_from = read_date("Дата від (YYYY-MM-DD): ")
    date_to = read_date("Дата до (YYYY-MM-DD): ")
    if date_from > date_to:
        print("Дата 'від' не може бути пізніше дати 'до'.")
        return None
    return date_from, date_to


def _show_report_rows(rows: list[dict]) -> None:
    print_rows(rows, [
        ("id", "ID"),
        ("sale_date", "Дата"),
        ("employee", "Співробітник"),
        ("book", "Книга"),
        ("actual_price", "Продаж"),
        ("profit", "Прибуток"),
    ])


def reports_menu() -> None:
    while True:
        print("\n=== ЗВІТИ ===")
        print("1. Продажі за дату")
        print("2. Продажі за період")
        print("3. Продажі конкретного співробітника")
        print("4. Найбільш продавана книга за період")
        print("5. Найуспішніший продавець за період")
        print("6. Сумарний прибуток за період")
        print("7. Автор, який найбільше продається (бонус)")
        print("8. Жанр, який найбільше продається (бонус)")
        print("9. Експорт продажів за період у CSV")
        print("0. Назад")

        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            target = read_date("Дата (YYYY-MM-DD): ")
            _show_report_rows(reports.sales_by_date(target))
            pause()

        elif choice == "2":
            period = _period()
            if period:
                _show_report_rows(reports.sales_by_period(*period))
                pause()

        elif choice == "3":
            employee_id = read_int("ID співробітника: ", 1)
            employee = employees.get_employee(employee_id)
            if not employee:
                print("Співробітника не знайдено.")
            else:
                print(f"\nПродажі: {employee['full_name']}")
                _show_report_rows(reports.sales_by_employee(employee_id))
            pause()

        elif choice == "4":
            period = _period()
            if period:
                row = reports.top_book(*period)
                if row:
                    print(f"Книга: {row['title']}")
                    print(f"Автор: {row['author']}")
                    print(f"Кількість продажів: {row['sales_count']}")
                else:
                    print("За цей період продажів немає.")
                pause()

        elif choice == "5":
            period = _period()
            if period:
                row = reports.top_employee(*period)
                if row:
                    print(f"Продавець: {row['full_name']}")
                    print(f"Кількість продажів: {row['sales_count']}")
                    print(f"Сумарний прибуток: {money(row['total_profit'])}")
                else:
                    print("За цей період продажів немає.")
                pause()

        elif choice == "6":
            period = _period()
            if period:
                row = reports.total_profit(*period)
                print(f"Кількість продажів: {row['sales_count']}")
                print(f"Сумарний прибуток: {money(row['total_profit'])}")
                pause()

        elif choice == "7":
            period = _period()
            if period:
                row = reports.top_author(*period)
                if row:
                    print(f"Автор: {row['author']}")
                    print(f"Кількість продажів: {row['sales_count']}")
                else:
                    print("За цей період продажів немає.")
                pause()

        elif choice == "8":
            period = _period()
            if period:
                row = reports.top_genre(*period)
                if row:
                    print(f"Жанр: {row['genre']}")
                    print(f"Кількість продажів: {row['sales_count']}")
                else:
                    print("За цей період продажів немає.")
                pause()

        elif choice == "9":
            period = _period()
            if period:
                rows = reports.sales_by_period(*period)
                if not rows:
                    print("Немає даних для експорту.")
                else:
                    filename = f"sales_{period[0]}_{period[1]}.csv"
                    path = reports.export_to_csv(rows, filename)
                    print(f"Експорт готовий: {path}")
                pause()

        elif choice == "0":
            return
        else:
            print("Невідомий пункт меню.")


def main_menu() -> None:
    while True:
        print("\n" + "=" * 48)
        print("      ОБЛІК ПРОДАЖУ КНИГ — PYTHON EXAM")
        print("=" * 48)
        print("1. Співробітники")
        print("2. Книги")
        print("3. Продажі")
        print("4. Звіти")
        print("0. Вихід")

        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            employees_menu()
        elif choice == "2":
            books_menu()
        elif choice == "3":
            sales_menu()
        elif choice == "4":
            reports_menu()
        elif choice == "0":
            print("До побачення!")
            return
        else:
            print("Невідомий пункт меню.")
