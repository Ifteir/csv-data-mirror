import json
from pathlib import Path
import yaml


def load_rules_json(rules_path: str) -> dict:
    path = Path(rules_path)
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if "columns" not in data or not isinstance(data["columns"], dict):
        raise ValueError("rules.json ফাইলে 'columns' ডিকশনারি থাকা আবশ্যক।")

    return {
        "secret_salt": data.get("secret_salt", "default-salt"),
        "amount_jitter_pct": float(data.get("amount_jitter_pct", 0.15)),
        "columns": data["columns"],
    }


def load_rules_yaml(rules_path: str) -> dict:
    path = Path(rules_path)
    with path.open("r", encoding="utf-8-sig") as f:
        data = yaml.safe_load(f) or {}

    if "columns" not in data or not isinstance(data["columns"], dict):
        raise ValueError("rules.yaml ফাইলে 'columns' ডিকশনারি থাকা আবশ্যক।")

    return {
        "secret_salt": data.get("secret_salt", "default-salt"),
        "amount_jitter_pct": float(data.get("amount_jitter_pct", 0.15)),
        "columns": data["columns"],
    }


def load_rules(rules_path: str) -> dict:
    ext = Path(rules_path).suffix.lower()
    if ext == ".json":
        return load_rules_json(rules_path)
    if ext in {".yaml", ".yml"}:
        return load_rules_yaml(rules_path)
    raise ValueError(f"অসমর্থিত রুল ফাইল ফরম্যাট: {ext}")
