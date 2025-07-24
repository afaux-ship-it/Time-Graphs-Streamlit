"""Datetime utilities sub-package.

This package breaks the original monolithic ``data_parser.py`` into
single-responsibility components that can be tested and extended
independently.

Public API:
    DateColumnDetector – find probable datetime columns
    DateParser        – convert a column to pandas ``datetime64``
    DateValidator     – check integrity/quality of parsed dates

Convenience helper ``detect_and_parse`` is provided for one-shot usage.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd

from .detector import DateColumnDetector
from .parser import DateParser
from .validator import DateValidator

__all__ = [
    "DateColumnDetector",
    "DateParser",
    "DateValidator",
    "detect_and_parse",
]


def detect_and_parse(
    df: pd.DataFrame,
    detector: DateColumnDetector | None = None,
    parser: DateParser | None = None,
) -> Tuple[pd.DataFrame, Dict[str, Dict]]:
    """Detect datetime columns, parse them, return new df and report.

    Returns
    -------
    df_parsed: DataFrame with detected columns converted to datetime
    report: mapping of column → {'parsed': bool, 'errors': list[str]}
    """
    detector = detector or DateColumnDetector()
    parser = parser or DateParser()

    candidates = detector.detect(df)
    report: Dict[str, Dict] = {}
    new_df = df.copy()

    for cand in candidates:
        col = cand["column"]
        parsed_series, errs = parser.parse(new_df[col], cand["format_hint"])
        if not parsed_series.isna().all():
            new_df[col] = parsed_series
            report[col] = {"parsed": True, "errors": errs}
        else:
            report[col] = {"parsed": False, "errors": errs}

    return new_df, report
