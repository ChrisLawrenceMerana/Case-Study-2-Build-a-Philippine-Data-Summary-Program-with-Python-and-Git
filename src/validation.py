"""Module for pipeline validation, reconciliation, and audit logging."""

import hashlib
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional
import pandas as pd

class AuditLogger:
    """Records pipeline steps and row-count transitions without modifying raw data."""

    def __init__(self):
        self.records: List[Dict[str, Any]] = []
        self._step_counter = 1

    def log(
        self,
        operation: str,
        rule: str,
        rows_before: int,
        rows_after: int,
    ) -> None:
        self.records.append(
            {
                "step": self._step_counter,
                "operation": operation,
                "rule": rule,
                "rows_before": rows_before,
                "rows_after": rows_after,
            }
        )
        self._step_counter += 1

    def to_csv(self, output_path: Path) -> pd.DataFrame:
        df_audit = pd.DataFrame(self.records)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_audit.to_csv(output_path, index=False)
        return df_audit

class PipelineValidator:
    """Executes reconciliation checks, floating-point comparisons, and asserts integrity."""

    def __init__(self):
        self.checks: List[Dict[str, Any]] = []

    def record_check(
        self,
        name: str,
        expected: Any,
        actual: Any,
        tolerance: float = 0.0,
    ) -> bool:
        """Evaluate a check with exact match for counts/strings or tolerance for floats."""
        if isinstance(expected, (int, str)) and isinstance(actual, (int, str)):
            passed = expected == actual
        else:
            exp_flt = float(expected)
            act_flt = float(actual)
            passed = math.isclose(exp_flt, act_flt, abs_tol=tolerance, rel_tol=0.0)

        self.checks.append(
            {
                "check": name,
                "expected": expected,
                "actual": actual,
                "tolerance": tolerance,
                "pass": passed,
            }
        )

        if not passed:
            print(
                f"\n[FATAL VALIDATION ERROR] Check '{name}' failed!\n"
                f"  - Expected:  {expected}\n"
                f"  - Actual:    {actual}\n"
                f"  - Tolerance: {tolerance}\n",
                file=sys.stderr,
            )
            # Dump current validation state before exiting
            sys.exit(1)

        return passed

    def to_csv(self, output_path: Path) -> pd.DataFrame:
        df_val = pd.DataFrame(self.checks)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_val.to_csv(output_path, index=False)
        return df_val