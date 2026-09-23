from typing import Optional
import pandas as pd

def top10(grouped_df: pd.DataFrame, sort_col: str='measure_sum', output_path: Optional[str]='top10.csv',) -> pd.DataFrame:
    top10_df = grouped_df.sort_values(by=sort_col, ascending=False).head(10)

    if output_path:
        top10_df.to_csv(output_path, index=False)
    return top10_df
