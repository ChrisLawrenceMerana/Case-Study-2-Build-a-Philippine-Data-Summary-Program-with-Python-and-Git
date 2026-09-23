"""Module for data processing, filtering, and summary generation."""

from typing import List, Optional
import pandas as pd


def generate_grouped_summary(
    df: pd.DataFrame,
    group_col: str = "countryorigin_iso3",
    measure_col: str = "dutiablevaluephp",
    output_path: Optional[str] = "output/grouped.csv",
) -> pd.DataFrame:
    """Group filtered customs data by category and compute summary metrics.

    Calculates the total row count, valid measure count, sum, and mean
    for the specified numerical measure per category group. Explicitly handles
    missing category values as a distinct group without dropping them.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered DataFrame containing customs records.
    group_col : str, default "countryorigin_iso3"
        The categorical column name used for grouping.
    measure_col : str, default "dutiablevaluephp"
        The numerical column name to aggregate.
    output_path : Optional[str], default "output/grouped.csv"
        File path to save the generated CSV. If None, file is not written.

    Returns
    -------
    pd.DataFrame
        Summary table indexed by the grouping category with aggregated metrics.
    """
    # Ensure missing categorical values are preserved
    working_df = df.copy()
    working_df[group_col] = working_df[group_col].fillna("MISSING").astype(str)

    # Perform named aggregations
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
        grouped_df.to_csv(output_path, index=False)

    return grouped_df


def generate_grouped_two_summary(
    df: pd.DataFrame,
    group_cols: Optional[List[str]] = None,
    measure_col: str = "dutiablevaluephp",
    output_path: Optional[str] = "output/grouped_two.csv",
) -> pd.DataFrame:

    """Groups by two categories and shows row counts and measure sums.

    Parameters:
    df: pd.DataFrame
        - Dataset containing customs records.
    group_cols: list of str, optional
        - Categorical columns for grouping. Defaults to ["countryorigin_iso3", "tq"].
    measure_col: str, default "dutiablevaluephp"
        - Numerical column to aggregate.
    output_path: str, optional
        - CSV destination path. If None, file export is skipped.

    Returns:
    pd.DataFrame
        - Aggregated summary table indexed by the grouping categories."""
    
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
        grouped_two_df.to_csv(output_path, index=False)

    return grouped_two_df