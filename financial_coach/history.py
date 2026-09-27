"""Local run history, persisted to a JSON file next to the project.

Not sent anywhere and not part of the analysis itself - purely a record
of past runs on this machine, shown as a table in the UI.
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_PATH = os.path.join(_PROJECT_ROOT, ".financial_coach_history.json")
MAX_ENTRIES = 50


def _verdict(surplus: float, total_debt: float) -> str:
    if surplus < 0:
        return "Deficit"
    if total_debt > 0 and surplus < total_debt * 0.02:
        return "Tight Budget"
    return "Healthy Surplus"


def _read_all() -> List[Dict[str, Any]]:
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def load_history(limit: int = 10) -> List[Dict[str, Any]]:
    """Most recent entries first."""
    return list(reversed(_read_all()))[:limit]


def append_history(monthly_income: float, total_expenses: float, total_debt: float) -> None:
    surplus = monthly_income - total_expenses
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "monthly_income": monthly_income,
        "total_expenses": total_expenses,
        "total_debt": total_debt,
        "surplus": surplus,
        "verdict": _verdict(surplus, total_debt),
    }
    data = _read_all()
    data.append(entry)
    data = data[-MAX_ENTRIES:]
    with open(HISTORY_PATH, "w") as f:
        json.dump(data, f, indent=2)
