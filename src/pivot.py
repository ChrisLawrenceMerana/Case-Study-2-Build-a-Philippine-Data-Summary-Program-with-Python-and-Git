from pathlib import Path
import pandas as pd


def build_pivot_table(
    df: pd.DataFrame,
    index_col: str,
    columns_col: str,
    value_col: str,
    output_path: str = "outputs/pivot.csv",
    missing_label: str = "Missing",
) -> pd.DataFrame:
    required = {index_col, columns_col, value_col}
    missing_cols = required - set(df.columns)
    if missing_cols:
        raise KeyError(
            f"build_pivot_table: missing required column(s): {sorted(missing_cols)}"
        )

    working = df[[index_col, columns_col, value_col]].copy()
    working[index_col] = working[index_col].fillna(missing_label)
    working[columns_col] = working[columns_col].fillna(missing_label)

    pivot = pd.pivot_table(
        working,
        index=index_col,
        columns=columns_col,
        values=value_col,
        aggfunc="sum",
        margins=True,
        margins_name="Total",
        fill_value=0,
    )

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pivot.to_csv(out_path)
    return pivot

def pivot_interior_sum(pivot: pd.DataFrame, margin_label: str = "Total") -> float:
    """Sum interior cells of a margins-included pivot table for validation."""
    interior = (
        pivot.drop(index=margin_label, errors="ignore")
        .drop(columns=margin_label, errors="ignore")
    )
    return float(interior.to_numpy().sum())
