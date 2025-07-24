"""Validate parsed datetime columns."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .core import DateTimeParser

__all__ = ["DateValidator"]


class DateValidator:
    """Check quality/integrity of a datetime Series."""

    def __init__(self):
        self._impl = DateTimeParser()

    def validate(self, series: pd.Series) -> Dict[str, Any]:
        return self._impl.validate_datetime_column(series)
