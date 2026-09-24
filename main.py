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
from graphs import plot_pivot_heatmap, plot_top10_bar
from pivot import build_pivot_table
from processor import generate_grouped_summary, generate_grouped_two_summary
from top10 import top10

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

def run_pipeline() -> None:
    """Execute the end-to-end data pipeline and generate all deliverables."""
    df = load_and_validate_data()

    output_dir = Path(config.OUTPUT_DIR).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. grouped.csv (group by the first category; row count, valid count, sum, mean)
    grouped_out = output_dir / "grouped.csv"
    grouped_df = generate_grouped_summary(
        df,
        group_col=config.GROUP_COL_ONE,
        measure_col=config.MEASURE_COL,
        output_path=str(grouped_out),
    )
    print(f"Created: {grouped_out}")

    # 2. grouped_two.csv (group by both categories; row count, sum using named aggregations)
    grouped_two_out = output_dir / "grouped_two.csv"
    grouped_two_df = generate_grouped_two_summary(
        df,
        group_cols=config.GROUP_COLS_TWO,
        measure_col=config.MEASURE_COL,
        output_path=str(grouped_two_out),
    )
    print(f"Created: {grouped_two_out}")

    # 3. pivot.csv (pivot_table of measure sum across categories, including margins)
    pivot_out = output_dir / "pivot.csv"
    pivot_df = build_pivot_table(
        df,
        index_col=config.GROUP_COLS_TWO[0],
        columns_col=config.GROUP_COLS_TWO[1],
        value_col=config.MEASURE_COL,
        output_path=str(pivot_out),
    )
    print(f"Created: {pivot_out}")

    # 4. top10.csv (top 10 groups by measure sum)
    top10_out = output_dir / "top10.csv"
    top10_df = top10(
        grouped_df,
        sort_col="measure_sum",
        output_path=str(top10_out),
    )
    print(f"Created: {top10_out}")

    # 5. bar.png (Matplotlib bar chart of top10 values)
    bar_out = output_dir / "bar.png"
    plot_top10_bar(top10_df, output_path=str(bar_out))
    print(f"Created: {bar_out}")

    # 6. heatmap.png (Seaborn heatmap of pivot.csv, margins excluded)
    heatmap_out = output_dir / "heatmap.png"
    plot_pivot_heatmap(pivot_df, margin_label="Total", output_path=str(heatmap_out))
    print(f"Created: {heatmap_out}")

    print(f"\nAll deliverables successfully generated in: {output_dir}")

if __name__ == "__main__":
    run_pipeline()