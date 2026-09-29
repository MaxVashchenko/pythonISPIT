from decimal import Decimal


def money(value) -> str:
    if value is None:
        return "0.00"
    return f"{Decimal(value):.2f} грн"


def print_rows(rows: list[dict], columns: list[tuple[str, str]]) -> None:
    if not rows:
        print("Даних немає.")
        return

    widths = []
    for key, title in columns:
        max_value = max(len(str(row.get(key, ""))) for row in rows)
        widths.append(max(len(title), max_value))

    header = " | ".join(title.ljust(widths[i]) for i, (_, title) in enumerate(columns))
    separator = "-+-".join("-" * width for width in widths)

    print(header)
    print(separator)
    for row in rows:
        print(" | ".join(str(row.get(key, "")).ljust(widths[i]) for i, (key, _) in enumerate(columns)))
