"""Detect potential datetime columns in a DataFrame.

This wraps the existing logic from ``utils.data_parser.DateTimeParser`` so we
can migrate incrementally without duplicating code.
"""
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from .core import DateTimeParser  # reuse proven implementation

__all__ = ["DateColumnDetector"]


class DateColumnDetector:
    """Find probable datetime columns.

    Example
    -------
    >>> detector = DateColumnDetector()
    >>> detector.detect(df)  # returns list[dict]
    """

    def __init__(self):
        self._impl = DateTimeParser()

    # Delegates ----------------------------------------------------------------
    def detect(self, df: pd.DataFrame, sample_size: int = 100) -> List[Dict[str, Any]]:
        """Return detection report (delegates to original parser)."""
        return self._impl.detect_datetime_columns(df, sample_size=sample_size)
