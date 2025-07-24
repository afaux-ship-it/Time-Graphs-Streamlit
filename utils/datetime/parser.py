"""Parse a series into pandas ``datetime64``.

Currently delegates to the existing ``DateTimeParser``. In future we can
replace internal logic without changing callers.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import pandas as pd

from .core import DateTimeParser

__all__ = ["DateParser"]


class DateParser:
    """Convert strings/ints to datetime."""

    def __init__(self):
        self._impl = DateTimeParser()

    def parse(
        self,
        series: pd.Series,
        format_hint: Optional[str] = None,
        custom_format: Optional[str] = None,
    ) -> Tuple[pd.Series, List[str]]:
        return self._impl.parse_datetime_column(series, format_hint, custom_format)
