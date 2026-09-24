"""Configuration settings for customs data loading and processing."""

from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# 1. Input path
INPUT_PATH = BASE_DIR / "2015.csv"

# 2. Output folder
OUTPUT_DIR = BASE_DIR / "output"

# 3. Grouping and measure columns
GROUP_COL_ONE = "countryorigin_iso3"
GROUP_COLS_TWO = ["countryorigin_iso3", "tq"]
MEASURE_COL = "dutiablevaluephp"

# 4. Filter values (Set to None or an empty dict to skip filtering)
# Example: {"tq": ["2015q1", "2015q2"]} or None
FILTERS = None