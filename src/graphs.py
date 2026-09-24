"""Module for generating visualization charts."""

from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def plot_top10_bar(
    top10_df: pd.DataFrame,
    category_col: Optional[str] = None,
    value_col: str = "measure_sum",
    output_path: str = "bar.png",
) -> None:
    """Generate a Matplotlib bar chart of top10.csv values."""
    if category_col is None:
        category_col = top10_df.columns[0]

    plt.figure(figsize=(10, 6))
    plt.bar(
        top10_df[category_col].astype(str),
        top10_df[value_col],
        color="#2b5c8f",
        edgecolor="black",
        linewidth=0.8,
    )
    plt.title(f"Top 10 by {value_col}", fontsize=14, weight="bold")
    plt.xlabel(category_col, fontsize=11)
    plt.ylabel(value_col, fontsize=11)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, dpi=300)
    plt.close()

def plot_pivot_heatmap(
    pivot_df: pd.DataFrame,
    margin_label: str = "Total",
    output_path: str = "heatmap.png",
) -> None:
    """Generate a Seaborn heatmap of pivot.csv, excluding margins."""
    interior = pivot_df.drop(index=margin_label, errors="ignore").drop(
        columns=margin_label, errors="ignore"
    )

    # Dynamically scale height so countries do not squash together
    plot_height = max(8, len(interior) * 0.25)
    plt.figure(figsize=(10, plot_height))

    sns.heatmap(
        interior.astype(float),
        annot=False,  # Clean matrix view without overlapping scientific notation
        cmap="YlGnBu",
        cbar=True,
        linewidths=0.5,
        linecolor="white",
    )
    plt.title("Pivot Heatmap (Interior / Margins Excluded)", fontsize=14, weight="bold")
    plt.xlabel("tq", fontsize=11)
    plt.ylabel("countryorigin_iso3", fontsize=11)
    plt.tight_layout()

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, dpi=300)
    plt.close()