import sys

from cli import main_menu
from database import init_db


def main() -> None:
    try:
        init_db()
        main_menu()
    except KeyboardInterrupt:
        print("\nРоботу програми перервано користувачем.")
    except Exception as exc:
        print("\nНе вдалося запустити програму.")
        print(f"Причина: {exc}")
        print("Перевірте PostgreSQL та параметри у файлі .env.")
        sys.exit(1)


if __name__ == "__main__":
    main()
