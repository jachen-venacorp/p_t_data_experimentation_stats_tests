"""Load a CSV and produce a matrix of distinct account counts by
`integration_status` and `account_typ_nm`.

Fill in `CSV_PATH` with the path to your file before running.
"""

from typing import Optional
import sys
from pathlib import Path
import argparse

import pandas as pd


# Use a raw string or Path to avoid escape-sequence issues in Windows paths.
source1 = r"C:\Users\JasonChen\OneDrive - Vena\Product Ops & Analytics\Advanced Analytics\flat file sources\integrations_relationships_0401v1.csv"


def load_csv(path: str) -> pd.DataFrame:
    """Load CSV at `path` into a pandas DataFrame."""
    return pd.read_csv(path)


def distinct_account_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return a matrix (DataFrame) counting distinct `account_id` for
    each combination of `integration_status` (index) and `account_typ_nm` (columns).
    """
    required = {"account_id", "integration_status", "account_typ_nm"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    mat = (
        df.groupby(["integration_status", "account_typ_nm"])["account_id"]
        .nunique()
        .unstack(fill_value=0)
    )
    return mat


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Load a CSV and produce a matrix of distinct account counts by "
            "integration_status and account_typ_nm."
        )
    )
    parser.add_argument("--source", "-s", help="Path to input CSV", default=source1)
    parser.add_argument("--out", "-o", help="Path to save matrix CSV (optional)")
    parser.add_argument("--pause", action="store_true", help="Pause before exit so you can inspect output")
    args = parser.parse_args()

    if not args.source:
        print("source is not set. Please set --source to the CSV file path.")
        return

    path = Path(args.source)
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    df = load_csv(str(path))
    mat = distinct_account_matrix(df)

    # Ensure pandas prints the full matrix to the console
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 0)

    # Print the full formatted table
    print(mat.to_string())

    # Save the matrix so it can be used in other tools (CSV)
    if args.out:
        out_path = Path(args.out)
    else:
        out_path = Path.cwd() / "integration_matrix_output.csv"

    try:
        mat.to_csv(out_path)
        print(f"Saved matrix to: {out_path}")
    except Exception as exc:  # pragma: no cover - simple I/O
        print(f"Failed to save matrix to {out_path}: {exc}")

    if args.pause:
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
