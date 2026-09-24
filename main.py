"""Main entry point orchestrating data validation, summary generation, and visualization."""

import sys
from pathlib import Path
import pandas as pd

# 1. Environment & Path Resolution
BASE_DIR = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
src_dir = BASE_DIR / "src"

# Ensure Python can discover modules inside the src/ directory
if src_dir.is_dir() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config

def load_and_validate_data() -> pd.DataFrame:
    """Load, validate schema, and filter customs data according to config specifications.

    Handles three edge cases with explicit error messages:
    1. Missing file: Raises FileNotFoundError if config.INPUT_PATH does not exist.
    2. Missing required columns: Raises KeyError detailing missing fields vs available columns.
    3. Filter returning 0 rows: Raises ValueError if filter criteria produce an empty DataFrame.
    """
    input_file = Path(config.INPUT_PATH).resolve()

    # Case 1: Missing file
    if not input_file.is_file():
        raise FileNotFoundError(
            f"[Error: Missing File] The specified dataset does not exist: '{input_file}'. "
            f"Please verify config.INPUT_PATH."
        )

    try:
        df = pd.read_csv(input_file, encoding="latin1", low_memory=False)
    except Exception as exc:
        raise RuntimeError(
            f"[Error: File Read Failure] Failed to read '{input_file}': {exc}"
        ) from exc

    # Case 2: Missing required column(s)
    required_cols = {config.GROUP_COL_ONE, config.MEASURE_COL}.union(
        set(config.GROUP_COLS_TWO)
    )
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise KeyError(
            f"[Error: Missing Required Column(s)] Missing: {sorted(missing_cols)}. "
            f"Columns present in dataset: {sorted(df.columns.tolist())}."
        )

    # Case 3: Filter returning no rows
    if getattr(config, "FILTERS", None):
        for filter_col, allowed_values in config.FILTERS.items():
            if filter_col not in df.columns:
                raise KeyError(
                    f"[Error: Invalid Filter Column] Filter column '{filter_col}' "
                    f"does not exist in the dataset."
                )
            df = df[df[filter_col].isin(allowed_values)]

        if df.empty:
            raise ValueError(
                f"[Error: Filter Returned No Rows] The filter criteria {config.FILTERS} "
                f"matched 0 records. Processing halted to avoid empty outputs."
            )

    return df