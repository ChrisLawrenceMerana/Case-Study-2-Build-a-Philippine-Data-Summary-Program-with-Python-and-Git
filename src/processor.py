"""Module for data processing, filtering, and summary generation."""

from pathlib import Path
from typing import List, Optional
import pandas as pd

def generate_grouped_summary(
    df: pd.DataFrame,
    group_col: str = "countryorigin_iso3",
    measure_col: str = "dutiablevaluephp",
    output_path: Optional[str] = "output/grouped.csv",
) -> pd.DataFrame:
    """Group by the first category; show row count, valid measure count, sum, and mean."""
    working_df = df.copy()
    working_df[group_col] = working_df[group_col].fillna("MISSING").astype(str)

    grouped_df = (
        working_df.groupby(group_col, dropna=False)
        .agg(
            row_count=(measure_col, "size"),
            valid_measure_count=(measure_col, "count"),
            measure_sum=(measure_col, "sum"),
            measure_mean=(measure_col, "mean"),
        )
        .reset_index()
    )

    if output_path:
        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
        grouped_df.to_csv(out_file, index=False)

    return grouped_df

def generate_grouped_two_summary(
    df: pd.DataFrame,
    group_cols: Optional[List[str]] = None,
    measure_col: str = "dutiablevaluephp",
    output_path: Optional[str] = "output/grouped_two.csv",
) -> pd.DataFrame:
    """Group by both categories; show row count and measure sum using named aggregations."""
    if group_cols is None:
        group_cols = ["countryorigin_iso3", "tq"]

    working_df = df.copy()
    working_df[group_cols] = working_df[group_cols].fillna("MISSING").astype(str)

    grouped_two_df = (
        working_df.groupby(group_cols, dropna=False)
        .agg(
            row_count=(measure_col, "size"),
            measure_sum=(measure_col, "sum"),
        )
        .reset_index()
    )

    if output_path:
        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
        grouped_two_df.to_csv(out_file, index=False)

    return grouped_two_df