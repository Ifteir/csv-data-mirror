import csv
import hashlib
import random
from pathlib import Path
from rule_loader import load_rules

FAKE_FIRST_NAMES = ["Arafat", "Nadia", "Tanvir", "Mim", "Rashed", "Sadia", "Fahim", "Tisha"]
FAKE_LAST_NAMES = ["Rahman", "Islam", "Hossain", "Akter", "Chowdhury", "Hasan"]
FAKE_CITIES = ["Dhaka", "Chattogram", "Sylhet", "Rajshahi", "Khulna"]


def clean_col_name(name: str) -> str:
    return name.lstrip("\ufeff").strip()


def deterministic_index(value: str, size: int, salt: str) -> int:
    digest = hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()
    return int(digest, 16) % size


def mask_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 4:
        return "***"
    return f"{digits[:3]}***{digits[-3:]}"


def fake_email(original_email: str, salt: str) -> str:
    idx = deterministic_index(original_email.strip().lower(), 9999, salt)
    return f"user{idx}@example.test"


def fake_name(original_name: str, salt: str) -> str:
    first = FAKE_FIRST_NAMES[deterministic_index(original_name + "_f", len(FAKE_FIRST_NAMES), salt)]
    last = FAKE_LAST_NAMES[deterministic_index(original_name + "_l", len(FAKE_LAST_NAMES), salt)]
    return f"{first} {last}"


def jitter_amount(value_str: str, pct: float = 0.15) -> str:
    try:
        num = float(value_str)
        factor = random.uniform(1 - pct, 1 + pct)
        new_num = num * factor
        if value_str.strip().isdigit():
            return str(round(new_num))
        return f"{new_num:.2f}"
    except ValueError:
        return value_str


def sanitize_row(row: dict, column_rules: dict, salt: str, jitter_pct: float) -> tuple[dict, list[str]]:
    new_row = {}
    unknown_cols = []

    for col, val in row.items():
        rule = column_rules.get(col)
        if rule is None:
            unknown_cols.append(col)
            new_row[col] = "[UNMAPPED]"
            continue

        if val is None or val == "":
            new_row[col] = val
        elif rule == "keep":
            new_row[col] = val
        elif rule == "name":
            new_row[col] = fake_name(val, salt)
        elif rule == "email":
            new_row[col] = fake_email(val, salt)
        elif rule == "phone":
            new_row[col] = mask_phone(val)
        elif rule == "city":
            new_row[col] = FAKE_CITIES[deterministic_index(val, len(FAKE_CITIES), salt)]
        elif rule == "amount":
            new_row[col] = jitter_amount(val, jitter_pct)
        elif rule == "drop":
            new_row[col] = ""
        else:
            new_row[col] = "[UNKNOWN_RULE]"

    return new_row, unknown_cols


def mirror_csv(input_path: str, output_path: str, rules_file: str) -> None:
    config = load_rules(rules_file)
    salt = config["secret_salt"]
    jitter_pct = config["amount_jitter_pct"]
    column_rules = {clean_col_name(k): v for k, v in config["columns"].items()}

    in_file = Path(input_path)
    out_file = Path(output_path)

    with in_file.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        raw_fieldnames = reader.fieldnames or []
        fieldnames = [clean_col_name(col) for col in raw_fieldnames]
        rows = [
            {clean_col_name(col): val for col, val in row.items()}
            for row in reader
        ]

    sanitized_rows = []
    flagged_columns = set()

    for row in rows:
        clean_row, unknown = sanitize_row(row, column_rules, salt, jitter_pct)
        sanitized_rows.append(clean_row)
        flagged_columns.update(unknown)

    with out_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sanitized_rows)

    print(f"সম্পন্ন হয়েছে! মোট রো: {len(sanitized_rows)} | আউটপুট: {out_file}")
    if flagged_columns:
        print(f"সতর্কতা—এই কলামগুলোর রুল দেওয়া ছিল না: {sorted(flagged_columns)}")


if __name__ == "__main__":
    mirror_csv("input.csv", "output_fake.csv", "rules.json")
