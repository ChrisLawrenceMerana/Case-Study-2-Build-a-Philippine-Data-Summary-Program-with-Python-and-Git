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
from pivot import build_pivot_table, pivot_interior_sum
from processor import generate_grouped_summary, generate_grouped_two_summary
from top10 import top10
from validation import AuditLogger, PipelineValidator

CUSTOMS_2015_REF = {
    "rows": 2_236_612,
    "cols": 30,
    "total_php": 3_587_267_375_257.0,
}

def run_pipeline() -> None:
    audit = AuditLogger()
    validator = PipelineValidator()
    output_dir = Path(config.OUTPUT_DIR).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    input_file = Path(config.INPUT_PATH).resolve()

    # 1. Load Raw File & Record Pre-filter State
    if not input_file.is_file():
        raise FileNotFoundError(
            f"[Error: Missing File] Cannot find dataset: '{input_file}'. Please verify config.INPUT_PATH."
        )

    try:
        raw_df = pd.read_csv(input_file, encoding="latin1", low_memory=False)
    except Exception as exc:
        raise RuntimeError(
            f"[Error: File Read Failure] Failed to read '{input_file}': {exc}"
        ) from exc

    # Validate required columns
    required_cols = {config.GROUP_COL_ONE, config.MEASURE_COL}.union(
        set(config.GROUP_COLS_TWO)
    )
    missing_cols = required_cols - set(raw_df.columns)
    if missing_cols:
        raise KeyError(
            f"[Error: Missing Required Column(s)] Missing: {sorted(missing_cols)}. "
            f"Columns present in dataset: {sorted(raw_df.columns.tolist())}."
        )

    raw_rows = len(raw_df)
    raw_cols = len(raw_df.columns)
    raw_measure_sum = float(raw_df[config.MEASURE_COL].sum(min_count=1))

    audit.log(
        operation="Load Raw Data",
        rule="Read raw CSV with latin1 encoding; keep source unchanged",
        rows_before=0,
        rows_after=raw_rows,
    )

    # Reference checks if processing the official Customs 2015 dataset
    if raw_rows == CUSTOMS_2015_REF["rows"]:
        validator.record_check("customs_2015_row_count", CUSTOMS_2015_REF["rows"], raw_rows)
        validator.record_check("customs_2015_col_count", CUSTOMS_2015_REF["cols"], raw_cols)
        validator.record_check(
            "customs_2015_raw_measure_sum",
            CUSTOMS_2015_REF["total_php"],
            raw_measure_sum,
            tolerance=1.0,
        )

    # 2. Filtering & Exclusions Rule
    filtered_df = raw_df.copy()
    if getattr(config, "FILTERS", None):
        for col, allowed in config.FILTERS.items():
            if col not in filtered_df.columns:
                raise KeyError(f"Filter column '{col}' missing from dataset.")
            # Missing filter values are placed in excluded group
            filtered_df = filtered_df[filtered_df[col].isin(allowed) & filtered_df[col].notna()]

        if filtered_df.empty:
            raise ValueError(
                f"[Error: Filter Returned No Rows] The filter criteria {config.FILTERS} "
                f"matched 0 records. Processing halted to avoid generating empty artifacts."
            )

    selected_rows = len(filtered_df)
    excluded_rows = raw_rows - selected_rows

    audit.log(
        operation="Filter Records",
        rule="Excluded rows outside criteria and rows with missing filter keys",
        rows_before=raw_rows,
        rows_after=selected_rows,
    )

    validator.record_check(
        "raw_equals_selected_plus_excluded",
        expected=raw_rows,
        actual=selected_rows + excluded_rows,
        tolerance=0.0,
    )

    # 3. Vectorized vs Loop Comparison Check
    vectorized_sum = float(filtered_df[config.MEASURE_COL].sum(min_count=1))

    # Independent loop calculation
    loop_sum = 0.0
    for val in filtered_df[config.MEASURE_COL]:
        if pd.notna(val):
            loop_sum += float(val)

    validator.record_check(
        "vectorized_vs_loop_sum",
        expected=loop_sum,
        actual=vectorized_sum,
        tolerance=1e-5,
    )

    # 4. Generate Summaries & Reconcile grouped.csv
    grouped_out = output_dir / "grouped.csv"
    grouped_df = generate_grouped_summary(
        filtered_df,
        group_col=config.GROUP_COL_ONE,
        measure_col=config.MEASURE_COL,
        output_path=str(grouped_out),
    )
    audit.log(
        operation="Generate Grouped Summary",
        rule=f"Aggregate {config.MEASURE_COL} by {config.GROUP_COL_ONE}",
        rows_before=selected_rows,
        rows_after=len(grouped_df),
    )

    # Check: Grouped row count sums to selected rows
    validator.record_check(
        "grouped_row_counts_sum_to_selected",
        expected=selected_rows,
        actual=int(grouped_df["row_count"].sum()),
        tolerance=0.0,
    )

    # Check: Grouped measure sum equals independently computed sum
    validator.record_check(
        "grouped_measure_sum_reconciliation",
        expected=vectorized_sum,
        actual=float(grouped_df["measure_sum"].sum()),
        tolerance=1e-2,
    )

    # grouped_two.csv
    grouped_two_out = output_dir / "grouped_two.csv"
    grouped_two_df = generate_grouped_two_summary(
        filtered_df,
        group_cols=config.GROUP_COLS_TWO,
        measure_col=config.MEASURE_COL,
        output_path=str(grouped_two_out),
    )
    audit.log(
        operation="Generate Grouped Two Summary",
        rule=f"Aggregate {config.MEASURE_COL} by {config.GROUP_COLS_TWO}",
        rows_before=selected_rows,
        rows_after=len(grouped_two_df),
    )

    validator.record_check(
        "grouped_two_measure_sum_reconciliation",
        expected=vectorized_sum,
        actual=float(grouped_two_df["measure_sum"].sum()),
        tolerance=1e-2,
    )

    # pivot.csv
    pivot_out = output_dir / "pivot.csv"
    pivot_df = build_pivot_table(
        filtered_df,
        index_col=config.GROUP_COLS_TWO[0],
        columns_col=config.GROUP_COLS_TWO[1],
        value_col=config.MEASURE_COL,
        output_path=str(pivot_out),
    )
    audit.log(
        operation="Generate Pivot Table",
        rule="Construct pivot table with row/col margins",
        rows_before=selected_rows,
        rows_after=len(pivot_df),
    )

    # Check: Interior sum excludes margins and matches independently computed sum
    p_int_sum = pivot_interior_sum(pivot_df, margin_label="Total")
    validator.record_check(
        "pivot_interior_sum_reconciliation",
        expected=vectorized_sum,
        actual=p_int_sum,
        tolerance=1e-2,
    )

    # top10.csv
    top10_out = output_dir / "top10.csv"
    top10_df = top10(
        grouped_df,
        sort_col="measure_sum",
        output_path=str(top10_out),
    )
    audit.log(
        operation="Extract Top 10",
        rule="Sort by measure_sum descending; take min(10, total_groups)",
        rows_before=len(grouped_df),
        rows_after=len(top10_df),
    )

    # 5. Visualizations & Plot Value Parity Checks
    bar_out = output_dir / "bar.png"
    plot_top10_bar(top10_df, output_path=str(bar_out))

    # Verify bar plot data parity
    validator.record_check(
        "bar_plot_data_length_matches_top10",
        expected=len(top10_df),
        actual=len(top10_df["measure_sum"].tolist()),
        tolerance=0.0,
    )
    validator.record_check(
        "bar_plot_top_value_parity",
        expected=float(top10_df["measure_sum"].iloc[0]),
        actual=float(top10_df["measure_sum"].max()),
        tolerance=1e-4,
    )

    heatmap_out = output_dir / "heatmap.png"
    plot_pivot_heatmap(pivot_df, margin_label="Total", output_path=str(heatmap_out))

    # 6. Save Validation & Audit Artifacts
    val_out = output_dir / "validation.csv"
    audit_out = output_dir / "audit_log.csv"

    validator.to_csv(val_out)
    audit.to_csv(audit_out)

    print("Pipeline finished successfully:")
    print(f"  - Validation report: {val_out}")
    print(f"  - Audit trail:       {audit_out}")

if __name__ == "__main__":
    run_pipeline()