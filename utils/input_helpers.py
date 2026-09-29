import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_RE = re.compile(r"^[+\d][\d\s()\-]{6,24}$")
ISBN_RE = re.compile(r"^(?:\d{9}[\dXx]|\d{13})$")


def read_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Поле не може бути порожнім.")


def read_int(prompt: str, min_value: int | None = None, max_value: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Введіть ціле число.")
            continue

        if min_value is not None and value < min_value:
            print(f"Значення має бути не менше {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Значення має бути не більше {max_value}.")
            continue
        return value


def read_positive_decimal(prompt: str) -> Decimal:
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            value = Decimal(raw)
        except InvalidOperation:
            print("Введіть коректне число.")
            continue

        if value <= 0:
            print("Значення має бути більше 0.")
            continue
        return value.quantize(Decimal("0.01"))


def read_date(prompt: str) -> date:
    while True:
        raw = input(prompt).strip()
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("Невірний формат. Використовуйте YYYY-MM-DD.")


def read_email(prompt: str) -> str:
    while True:
        value = input(prompt).strip().lower()
        if EMAIL_RE.match(value):
            return value
        print("Некоректний email. Приклад: user@example.com")


def read_phone(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if PHONE_RE.match(value):
            return value
        print("Некоректний номер телефону.")


def read_isbn(prompt: str) -> str:
    while True:
        value = input(prompt).strip().replace("-", "").replace(" ", "")
        if ISBN_RE.match(value):
            return value.upper()
        print("ISBN має містити 10 або 13 символів (для ISBN-10 допускається X в кінці).")


def confirm(prompt: str = "Підтвердити? [y/n]: ") -> bool:
    while True:
        value = input(prompt).strip().lower()
        if value in {"y", "yes", "т", "так"}:
            return True
        if value in {"n", "no", "н", "ні"}:
            return False
        print("Введіть y або n.")


def optional_text(prompt: str, current: str) -> str:
    value = input(f"{prompt} [{current}]: ").strip()
    return value if value else current




def optional_isbn(prompt: str, current: str) -> str:
    while True:
        value = input(f"{prompt} [{current}]: ").strip().replace("-", "").replace(" ", "")
        if not value:
            return current
        if ISBN_RE.match(value):
            return value.upper()
        print("ISBN має містити 10 або 13 символів (для ISBN-10 допускається X в кінці).")

def optional_email(prompt: str, current: str) -> str:
    while True:
        value = input(f"{prompt} [{current}]: ").strip().lower()
        if not value:
            return current
        if EMAIL_RE.match(value):
            return value
        print("Некоректний email.")


def optional_phone(prompt: str, current: str) -> str:
    while True:
        value = input(f"{prompt} [{current}]: ").strip()
        if not value:
            return current
        if PHONE_RE.match(value):
            return value
        print("Некоректний номер телефону.")


def optional_int(prompt: str, current: int, min_value: int | None = None, max_value: int | None = None) -> int:
    while True:
        raw = input(f"{prompt} [{current}]: ").strip()
        if not raw:
            return current
        try:
            value = int(raw)
        except ValueError:
            print("Введіть ціле число.")
            continue
        if min_value is not None and value < min_value:
            print(f"Значення має бути не менше {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Значення має бути не більше {max_value}.")
            continue
        return value


def optional_decimal(prompt: str, current) -> Decimal:
    while True:
        raw = input(f"{prompt} [{current}]: ").strip().replace(",", ".")
        if not raw:
            return Decimal(str(current))
        try:
            value = Decimal(raw)
        except InvalidOperation:
            print("Введіть коректне число.")
            continue
        if value <= 0:
            print("Значення має бути більше 0.")
            continue
        return value.quantize(Decimal("0.01"))


def optional_date(prompt: str, current) -> date:
    current_text = current.isoformat() if hasattr(current, "isoformat") else str(current)
    while True:
        raw = input(f"{prompt} [{current_text}]: ").strip()
        if not raw:
            return current
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("Невірний формат. Використовуйте YYYY-MM-DD.")
