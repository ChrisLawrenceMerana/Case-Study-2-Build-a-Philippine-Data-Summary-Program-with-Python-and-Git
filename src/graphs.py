from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Base directory where files are stored
BASE_DIR = Path(__file__).resolve().parent

# 1. Bar Chart of top10.csv files
top10_file = BASE_DIR / "top10.csv"
df_top10 = pd.read_csv(top10_file)

# Extract first column name for category and sort column
category_col = df_top10.columns[0]
value_col = "measure_sum"

plt.figure(figsize=(10, 6))
plt.bar(
    df_top10[category_col].astype(str),
    df_top10[value_col],
    color="#2b5c8f",
    edgecolor="black",
    linewidth=0.8,
)
plt.title(f"Top 10 by {value_col}", fontsize=14, weight="bold")
plt.xlabel(category_col, fontsize=11)
plt.ylabel(value_col, fontsize=11)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

bar_out = BASE_DIR / "bar.png"
plt.savefig(bar_out, dpi=300)
plt.close()
print(f"Created: {bar_out.name}")