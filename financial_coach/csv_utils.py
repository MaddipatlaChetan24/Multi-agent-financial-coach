"""CSV parsing and validation for uploaded transaction data."""
import csv
from io import StringIO
from typing import Any, Dict, List, Tuple

import pandas as pd

REQUIRED_COLUMNS = ["Date", "Category", "Amount"]


def validate_csv_format(file) -> Tuple[bool, str]:
    """Validate CSV file format and content."""
    try:
        content = file.read().decode("utf-8")
        has_header = csv.Sniffer().has_header(content)
        file.seek(0)

        if not has_header:
            return False, "CSV file must have headers"

        df = pd.read_csv(StringIO(content))
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"

        try:
            pd.to_datetime(df["Date"])
        except Exception:
            return False, "Invalid date format in Date column"

        try:
            df["Amount"].replace(r"[\$,]", "", regex=True).astype(float)
        except Exception:
            return False, "Invalid amount format in Amount column"

        return True, "CSV format is valid"
    except Exception as e:
        return False, f"Invalid CSV format: {str(e)}"


def parse_csv_transactions(file_content: bytes) -> Dict[str, Any]:
    """Parse CSV file content into transactions plus category totals."""
    try:
        df = pd.read_csv(StringIO(file_content.decode("utf-8")))

        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        df["Amount"] = df["Amount"].replace(r"[\$,]", "", regex=True).astype(float)

        category_totals = df.groupby("Category")["Amount"].sum().reset_index()

        return {
            "transactions": df.to_dict("records"),
            "category_totals": category_totals.to_dict("records"),
        }
    except Exception as e:
        raise ValueError(f"Error parsing CSV file: {str(e)}")


def monthly_category_trend(transactions: List[Dict[str, Any]], top_n: int = 6) -> pd.DataFrame:
    """Pivot transactions into a month x category spending trend table.

    Only useful when the CSV spans more than one month; categories beyond
    the top `top_n` (by total spend) are folded into "Other" so the chart
    stays readable.
    """
    if not transactions:
        return pd.DataFrame()

    df = pd.DataFrame(transactions)
    if "Date" not in df.columns or "Category" not in df.columns or "Amount" not in df.columns:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    if df["Month"].nunique() < 2:
        return pd.DataFrame()

    top_categories = df.groupby("Category")["Amount"].sum().sort_values(ascending=False).head(top_n).index
    df["Category"] = df["Category"].where(df["Category"].isin(top_categories), "Other")

    trend = df.groupby(["Month", "Category"])["Amount"].sum().reset_index()
    return trend.sort_values("Month")
