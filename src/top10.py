from typing import Optional
import pandas as pd

def top10(grouped_df: pd.DataFrame, sort_col: str='measure_sum', output_path: Optional[str]='top10.csv',) -> pd.DataFrame:
    top10_df = grouped_df.sort_values(by=sort_col, ascending=False).head(10)
    """Sorts the first grouped table by measure sum and maintains the ten largest ones.
    
    Parameters:
    grouped_df - Grouped summary DataFrame
    sort_col - Sum column used to sort and determine the largest among the grouped table.
    output_path - File path to save generated .csv file.

    Returns:
    pd.DataFrame - Post-filter DataFrame containing the ten largest groups of the grouped summary DataFrame.
    """

    if output_path:
        top10_df.to_csv(output_path, index=False)
    return top10_df
