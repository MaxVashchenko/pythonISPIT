#!/usr/bin/env python3
"""Автоматичний запуск екзаменаційного проєкту на macOS.

Сценарій:
1. знаходить PostgreSQL;
2. якщо PostgreSQL відсутній — встановлює його через Homebrew;
3. запускає PostgreSQL;
4. підключається до локального сервера;
5. створює БД book_sales;
6. створює .env;
7. створює .venv і встановлює залежності;
8. створює таблиці та демо-дані;
9. запускає CLI-застосунок.

Для стандартної інсталяції Homebrew додаткові налаштування не потрібні.
Якщо PostgreSQL використовує парольну автентифікацію, скрипт попросить
логін і пароль у терміналі.
"""

from __future__ import annotations

import getpass
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


PROJECT_DIR = Path(__file__).resolve().parent
VENV_DIR = PROJECT_DIR / ".venv"
ENV_FILE = PROJECT_DIR / ".env"
REQUIREMENTS = PROJECT_DIR / "requirements.txt"

DB_NAME = "book_sales"
DB_PORT = "5432"
POSTGRES_FORMULAS = (
    "postgresql@18",
    "postgresql@17",
    "postgresql@16",
    "postgresql@15",
    "postgresql@14",
    "postgresql",
)


class SetupError(RuntimeError):
    """Помилка автоматичного налаштування."""


def print_step(message: str) -> None:
    print(f"\n=== {message} ===")


def ok(message: str) -> None:
    print(f"✓ {message}")


def warn(message: str) -> None:
    print(f"! {message}")


def run(
    command: list[str],
    *,
    check: bool = True,
    capture_output: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PROJECT_DIR,
        check=check,
        text=True,
        capture_output=capture_output,
        env=env,
    )


def find_brew() -> str | None:
    candidates = [
        shutil.which("brew"),
        "/opt/homebrew/bin/brew",      # Apple Silicon
        "/usr/local/bin/brew",         # Intel Mac
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def brew_formula_installed(brew: str, formula: str) -> bool:
    result = run(
        [brew, "list", "--formula", formula],
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def find_homebrew_postgres(brew: str) -> tuple[str, Path] | None:
    for formula in POSTGRES_FORMULAS:
        if not brew_formula_installed(brew, formula):
            continue

        result = run(
            [brew, "--prefix", formula],
            capture_output=True,
        )
        prefix = Path(result.stdout.strip())
        if (prefix / "bin" / "psql").exists():
            return formula, prefix
    return None


def install_postgres_with_brew(brew: str) -> tuple[str, Path]:
    print_step("PostgreSQL не знайдено — встановлюю автоматично")

    # Спочатку пробуємо конкретну версію. Якщо формула недоступна,
    # використовуємо актуальну стандартну формулу Homebrew.
    for formula in ("postgresql@17", "postgresql"):
        print(f"Пробую: brew install {formula}")
        result = run([brew, "install", formula], check=False)
        if result.returncode == 0:
            prefix_result = run([brew, "--prefix", formula], capture_output=True)
            prefix = Path(prefix_result.stdout.strip())
            ok(f"Встановлено {formula}")
            return formula, prefix

    raise SetupError("Homebrew не зміг встановити PostgreSQL.")


def find_postgres_tools() -> tuple[Path, Path, Path | None, str | None, str | None]:
    """Повертає psql, createdb, pg_isready, тип інсталяції та formula."""
    psql = shutil.which("psql")
    createdb = shutil.which("createdb")
    pg_isready = shutil.which("pg_isready")

    if psql and createdb:
        return (
            Path(psql),
            Path(createdb),
            Path(pg_isready) if pg_isready else None,
            "path",
            None,
        )

    brew = find_brew()
    if brew:
        found = find_homebrew_postgres(brew)
        if found is None:
            found = install_postgres_with_brew(brew)

        formula, prefix = found
        psql_path = prefix / "bin" / "psql"
        createdb_path = prefix / "bin" / "createdb"
        pg_isready_path = prefix / "bin" / "pg_isready"

        if psql_path.exists() and createdb_path.exists():
            return (
                psql_path,
                createdb_path,
                pg_isready_path if pg_isready_path.exists() else None,
                "homebrew",
                formula,
            )

    postgres_app = Path("/Applications/Postgres.app/Contents/Versions/latest/bin")
    if (postgres_app / "psql").exists() and (postgres_app / "createdb").exists():
        pg_ready = postgres_app / "pg_isready"
        return (
            postgres_app / "psql",
            postgres_app / "createdb",
            pg_ready if pg_ready.exists() else None,
            "postgres_app",
            None,
        )

    if not brew:
        raise SetupError(
            "PostgreSQL не знайдено, а Homebrew не встановлений. "
            "Встановіть Homebrew один раз і повторіть: python3 start_exam.py"
        )

    raise SetupError("Не вдалося знайти утиліти PostgreSQL після встановлення.")


def postgres_ready(pg_isready: Path | None, psql: Path) -> bool:
    if pg_isready:
        result = run(
            [str(pg_isready), "-p", DB_PORT],
            check=False,
            capture_output=True,
        )
        return result.returncode == 0

    result = run(
        [str(psql), "-p", DB_PORT, "-d", "postgres", "-Atqc", "SELECT 1"],
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def start_postgres(
    psql: Path,
    pg_isready: Path | None,
    install_type: str | None,
    formula: str | None,
) -> None:
    print_step("Перевіряю PostgreSQL")

    if postgres_ready(pg_isready, psql):
        ok("PostgreSQL уже запущений")
        return

    if install_type == "homebrew":
        brew = find_brew()
        if not brew or not formula:
            raise SetupError("Не вдалося визначити Homebrew PostgreSQL service.")
        print(f"Запускаю: brew services start {formula}")
        result = run([brew, "services", "start", formula], check=False)
        if result.returncode != 0:
            raise SetupError(f"Не вдалося запустити Homebrew service {formula}.")

    elif install_type == "postgres_app":
        print("Запускаю Postgres.app...")
        result = run(["open", "-a", "Postgres"], check=False)
        if result.returncode != 0:
            raise SetupError("Не вдалося запустити Postgres.app.")

    else:
        # psql може бути у PATH, але сервер — Homebrew. Спробуємо знайти його.
        brew = find_brew()
        if brew:
            found = find_homebrew_postgres(brew)
            if found:
                formula_name, _ = found
                run([brew, "services", "start", formula_name], check=False)

    for _ in range(30):
        if postgres_ready(pg_isready, psql):
            ok("PostgreSQL готовий приймати підключення")
            return
        time.sleep(1)

    raise SetupError(
        "PostgreSQL встановлено, але сервер не запустився за 30 секунд."
    )


def connection_env(password: str) -> dict[str, str]:
    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password
    else:
        env.pop("PGPASSWORD", None)
    return env


def try_connection(psql: Path, user: str, host: str, password: str) -> bool:
    command = [
        str(psql),
        "-w",  # не дозволяємо psql самому питати пароль
        "-p",
        DB_PORT,
        "-U",
        user,
        "-d",
        "postgres",
        "-Atqc",
        "SELECT 1",
    ]
    if host:
        command[1:1] = ["-h", host]

    result = run(
        command,
        check=False,
        capture_output=True,
        env=connection_env(password),
    )
    return result.returncode == 0 and result.stdout.strip() == "1"


def resolve_admin_connection(psql: Path) -> tuple[str, str, str]:
    print_step("Підключаюся до PostgreSQL")

    os_user = getpass.getuser()
    if try_connection(psql, os_user, "", ""):
        ok(f"Підключено як PostgreSQL-користувач: {os_user}")
        return os_user, "", ""

    if try_connection(psql, "postgres", "", ""):
        ok("Підключено як PostgreSQL-користувач: postgres")
        return "postgres", "", ""

    warn("Для PostgreSQL потрібен пароль. Введіть його один раз — скрипт збереже його у локальний .env.")
    user = input("PostgreSQL admin user [postgres]: ").strip() or "postgres"
    password = getpass.getpass("PostgreSQL password: ")

    # Спочатку пробуємо локальний Unix socket — саме так зазвичай
    # підключається psql на macOS. Якщо не вийде — пробуємо TCP.
    for host in ("", "127.0.0.1"):
        if try_connection(psql, user, host, password):
            ok(f"Підключення успішне як {user}")
            return user, host, password

    raise SetupError("Невірний PostgreSQL login/password або сервер недоступний.")


def psql_query(
    psql: Path,
    *,
    database: str,
    user: str,
    host: str,
    password: str,
    sql: str,
) -> str:
    command = [
        str(psql),
        "-w",
        "-p",
        DB_PORT,
        "-U",
        user,
        "-d",
        database,
        "-Atqc",
        sql,
    ]
    if host:
        command[1:1] = ["-h", host]

    result = run(
        command,
        capture_output=True,
        env=connection_env(password),
    )
    return result.stdout.strip()


def create_database(
    psql: Path,
    createdb: Path,
    user: str,
    host: str,
    password: str,
) -> None:
    print_step(f"Перевіряю базу {DB_NAME}")

    exists = psql_query(
        psql,
        database="postgres",
        user=user,
        host=host,
        password=password,
        sql=f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';",
    )
    if exists == "1":
        ok(f"База {DB_NAME} уже існує")
        return

    command = [
        str(createdb),
        "-w",
        "-p",
        DB_PORT,
        "-U",
        user,
        DB_NAME,
    ]
    if host:
        command[1:1] = ["-h", host]

    run(command, env=connection_env(password))
    ok(f"Базу {DB_NAME} створено")


def env_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_env(user: str, host: str, password: str) -> None:
    print_step("Створюю .env")

    content = (
        f"DB_HOST={env_value(host)}\n"
        f"DB_PORT={DB_PORT}\n"
        f"DB_NAME={DB_NAME}\n"
        f"DB_USER={env_value(user)}\n"
        f"DB_PASSWORD={env_value(password)}\n"
    )
    ENV_FILE.write_text(content, encoding="utf-8")
    ok(".env створено автоматично")


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def prepare_python() -> Path:
    print_step("Готую Python середовище")

    if not VENV_DIR.exists():
        run([sys.executable, "-m", "venv", str(VENV_DIR)])
        ok("Створено .venv")
    else:
        ok(".venv уже існує")

    python = venv_python()
    if not python.exists():
        raise SetupError("Не знайдено Python усередині .venv.")

    print("Встановлюю Python-залежності...")
    run([str(python), "-m", "pip", "install", "-q", "-r", str(REQUIREMENTS)])
    ok("Залежності встановлено")
    return python


def initialize_project_database(python: Path) -> None:
    print_step("Створюю таблиці та демо-дані")
    run([str(python), "seed.py"])
    ok("База проєкту готова")


def run_application(python: Path) -> int:
    print_step("Усе готово — запускаю програму")

    print()
    print("😎 Невелика статистика розробки:")
    print("64% — робив сам")
    print("36% — GPT допомагав доточити хвости 😄")
    print()

    result = run([str(python), "main.py"], check=False)
    return result.returncode


def main() -> int:
    os.chdir(PROJECT_DIR)

    print("Облік продажу книг — автоматичний запуск")
    print(f"Папка проєкту: {PROJECT_DIR}")

    if sys.platform != "darwin":
        warn("Автоматичне встановлення PostgreSQL розраховане насамперед на macOS.")

    try:
        psql, createdb, pg_isready, install_type, formula = find_postgres_tools()
        ok(f"PostgreSQL tools: {psql}")

        start_postgres(psql, pg_isready, install_type, formula)
        user, host, password = resolve_admin_connection(psql)
        create_database(psql, createdb, user, host, password)
        write_env(user, host, password)

        python = prepare_python()
        initialize_project_database(python)
        return run_application(python)

    except KeyboardInterrupt:
        print("\nЗапуск перервано користувачем.")
        return 130
    except (SetupError, subprocess.CalledProcessError) as exc:
        print(f"\n✗ ПОМИЛКА: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
