# CSV Data Sanitizer & Fake Data Mirror

A lightweight Python CLI tool that sanitizes sensitive columns in CSV files and generates safe, schema-preserving fake data for testing, demos, and local development. It supports deterministic replacements (using a local secret salt) so repeated values stay consistent across rows, along with external rule configurations in **JSON** or **YAML**.

---

## Features

- **Schema & Header Preservation:** Keeps original CSV columns and row structure intact while safely transforming sensitive fields.
- **Deterministic Mirroring:** Uses a SHA-256 hash with a configurable `secret_salt` so identical inputs (such as names, emails, or cities) map consistently.
- **External Rule Files:** Configure column transformations in `rules.json` or `rules.yaml` without modifying Python code.
- **BOM-Safe Parsing:** Handles UTF-8 with BOM (`utf-8-sig`) gracefully—helpful for files created or edited on Windows.
- **Unmapped Column Guard:** Flags columns missing from your rule config as `[UNMAPPED]` so sensitive data is not accidentally passed through untouched.

---

## Project Structure

```text
data_mirror/
├── csv_mirror.py     # Main CSV sanitization and mirroring script
├── rule_loader.py    # Loads and validates rules from JSON or YAML files
├── rules.json        # Sample JSON rule configuration
├── rules.yaml        # Sample YAML rule configuration
├── input.csv         # Sample input CSV file
└── output_fake.csv   # Generated output file (created after running)
```

---

## Quick Start

### 1. Clone the Repository
```bash
git clone [https://github.com/](https://github.com/)<your-username>/csv-data-mirror.git
cd csv-data-mirror
```

### 2. Install Dependencies
Ensure **Python 3.10+** is installed. If you use YAML rule files (`rules.yaml`), install `PyYAML`:
```bash
pip install pyyaml
```

### 3. Configure Column Rules (`rules.json` or `rules.yaml`)
Define how each column should be processed:

**`rules.json`:**
```json
{
  "secret_salt": "change-this-to-your-own-secret-salt",
  "amount_jitter_pct": 0.15,
  "columns": {
    "id": "keep",
    "full_name": "name",
    "email": "email",
    "phone": "phone",
    "city": "city",
    "order_total": "amount",
    "status": "keep"
  }
}
```

**`rules.yaml`:**
```yaml
secret_salt: "change-this-to-your-own-secret-salt"
amount_jitter_pct: 0.15

columns:
  id: keep
  full_name: name
  email: email
  phone: phone
  city: city
  order_total: amount
  status: keep
```

### 4. Prepare Input CSV (`input.csv`)
```csv
id,full_name,email,phone,city,order_total,status
1,Rahim Uddin,rahim@gmail.com,01712345678,Dhaka,1200,paid
2,Karima Begum,karima@yahoo.com,01898765432,Sylhet,850.50,pending
```

### 5. Run the Script
```bash
python csv_mirror.py
```

This generates `output_fake.csv` with anonymized values while keeping the original structure intact:
```csv
id,full_name,email,phone,city,order_total,status
1,Rashed Hossain,user1945@example.test,017***678,Khulna,1259,paid
2,Nadia Hossain,user9588@example.test,018***432,Dhaka,957.74,pending
```

---

## Supported Column Rules

| Rule | Behavior |
| :--- | :--- |
| `keep` | Preserves the original value unchanged |
| `name` | Replaces with a deterministic synthetic name |
| `email` | Replaces with a deterministic `@example.test` address |
| `phone` | Masks middle digits while keeping prefix and suffix |
| `city` | Replaces with a deterministic sample city |
| `amount` | Adds random percentage jitter (`amount_jitter_pct`) to numeric values |
| `drop` | Clears the field value to an empty string (`""`) |

---

## Security Best Practices

Before pushing changes to GitHub, ensure real production CSVs and generated outputs are excluded via `.gitignore`:

```gitignore
__pycache__/
*.pyc
output_fake.csv
real_*.csv
```

---

## Roadmap

- [ ] Add CLI flags (`--input`, `--output`, `--rules`) via `argparse`
- [ ] Integrate `Faker` for richer synthetic data (addresses, companies, dates)
- [ ] Add unit tests with `pytest`