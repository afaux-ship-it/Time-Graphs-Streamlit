"""Core DateTimeParser implementation migrated from utils.data_parser.

This file is a verbatim copy (minus Streamlit imports) so the behaviour
remains identical.  All datetime sub-modules import ``DateTimeParser`` from
here, allowing us to remove the legacy ``utils/data_parser.py``.
"""
from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from dateutil import parser as date_parser
import pytz

import config

__all__ = ["DateTimeParser"]


class DateTimeParser:
    """Handles detection, parsing and validation of date/time columns."""

    DATE_PATTERNS = config.DATE_PATTERNS  # type: ignore[attr-defined]
    DATETIME_FORMATS = config.DATETIME_FORMATS  # type: ignore[attr-defined]

    def __init__(self):
        self.timezone = pytz.UTC

    # ------------------------------------------------------------------
    # Detection helpers
    # ------------------------------------------------------------------
    def detect_datetime_columns(self, df: pd.DataFrame, sample_size: int = 100) -> List[Dict[str, Any]]:
        datetime_candidates: List[Dict[str, Any]] = []
        sample_df = df.head(sample_size) if len(df) > sample_size else df

        for column in df.columns:
            if df[column].dtype == "object" or pd.api.types.is_string_dtype(df[column]):
                confidence, fmt_hint = self._analyze_column_for_datetime(sample_df[column].dropna())
                if confidence > 0.3:
                    datetime_candidates.append(
                        {
                            "column": column,
                            "confidence": confidence,
                            "format_hint": fmt_hint,
                            "sample_values": sample_df[column].dropna().head(3).tolist(),
                        }
                    )
            elif pd.api.types.is_numeric_dtype(df[column]):
                confidence, fmt_hint = self._check_unix_timestamp(sample_df[column].dropna())
                if confidence > 0.5:
                    datetime_candidates.append(
                        {
                            "column": column,
                            "confidence": confidence,
                            "format_hint": fmt_hint,
                            "sample_values": sample_df[column].dropna().head(3).tolist(),
                        }
                    )

        datetime_candidates.sort(key=lambda x: x["confidence"], reverse=True)
        return datetime_candidates

    # ------------------------------------------------------------------
    # Internal analysis helpers
    # ------------------------------------------------------------------
    def _analyze_column_for_datetime(self, series: pd.Series) -> Tuple[float, str]:
        if len(series) == 0:
            return 0.0, "No data"

        total = len(series)
        parsed_cnt = 0
        format_matches: Dict[str, int] = {}

        for val in series:
            if pd.isna(val):
                continue
            str_val = str(val).strip()
            for pattern in self.DATE_PATTERNS:
                if re.match(pattern, str_val):
                    format_matches[pattern] = format_matches.get(pattern, 0) + 1
                    break
            try:
                date_parser.parse(str_val)
                parsed_cnt += 1
            except (ValueError, TypeError, OverflowError):
                pass

        confidence = parsed_cnt / total if total else 0
        if format_matches:
            best_pattern = max(format_matches, key=format_matches.get)
            fmt_hint = self._pattern_to_format_hint(best_pattern)
        else:
            fmt_hint = "Mixed or custom format"
        return confidence, fmt_hint

    def _check_unix_timestamp(self, series: pd.Series) -> Tuple[float, str]:
        if len(series) == 0:
            return 0.0, "No data"
        min_val, max_val = series.min(), series.max()
        ranges = [
            (0, 2147483647, "Unix timestamp (seconds)"),
            (0, 2147483647000, "Unix timestamp (milliseconds)"),
            (315532800, 4102444800, "Unix timestamp (seconds, 1980-2100)"),
        ]
        confidence = 0.0
        fmt_hint = "Not a timestamp"
        for lo, hi, hint in ranges:
            if lo <= min_val <= hi and lo <= max_val <= hi:
                try:
                    test_date = (
                        pd.to_datetime(series.iloc[0], unit="ms") if max_val > 2147483647 else pd.to_datetime(series.iloc[0], unit="s")
                    )
                    if pd.Timestamp("1970-01-01") <= test_date <= pd.Timestamp("2050-01-01"):
                        confidence = 0.8
                        fmt_hint = hint
                        break
                except Exception:  # pylint: disable=broad-except
                    continue
        return confidence, fmt_hint

    @staticmethod
    def _pattern_to_format_hint(pattern: str) -> str:
        mapping = {
            r"\d{4}-\d{2}-\d{2}": "YYYY-MM-DD",
            r"\d{2}/\d{2}/\d{4}": "MM/DD/YYYY or DD/MM/YYYY",
            r"\d{2}-\d{2}-\d{4}": "MM-DD-YYYY or DD-MM-YYYY",
            r"\d{1,2}/\d{1,2}/\d{4}": "M/D/YYYY",
            r"\d{1,2}-\d{1,2}-\d{4}": "M-D-YYYY",
            r"\d{4}/\d{2}/\d{2}": "YYYY/MM/DD",
            r"\d{4}\d{2}\d{2}": "YYYYMMDD",
        }
        return mapping.get(pattern, "Custom format")

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def parse_datetime_column(
        self,
        series: pd.Series,
        format_hint: Optional[str] = None,
        custom_format: Optional[str] = None,
    ) -> Tuple[pd.Series, List[str]]:
        errors: List[str] = []
        if custom_format:
            try:
                parsed = pd.to_datetime(series, format=custom_format, errors="coerce")
                if not parsed.isna().all():
                    return parsed, errors
                errors.append(f"Custom format '{custom_format}' failed to parse any values")
            except Exception as exc:  # pylint: disable=broad-except
                errors.append(f"Custom format error: {exc}")

        if format_hint and "timestamp" in str(format_hint).lower():
            try:
                unit = "ms" if "milliseconds" in format_hint.lower() else "s"
                parsed = pd.to_datetime(series, unit=unit, errors="coerce")
                if not parsed.isna().all():
                    return parsed, errors
            except Exception as exc:  # pylint: disable=broad-except
                errors.append(f"Timestamp parsing error: {exc}")

        for fmt in self.DATETIME_FORMATS:
            try:
                parsed = pd.to_datetime(series, format=fmt, errors="coerce")
                success_rate = (len(parsed) - parsed.isna().sum()) / len(parsed)
                if success_rate >= 0.5:
                    return parsed, errors
            except Exception:  # pylint: disable=broad-except
                continue

        try:
            parsed = pd.to_datetime(series, errors="coerce", infer_datetime_format=True)
            success_rate = (len(parsed) - parsed.isna().sum()) / len(parsed)
            if success_rate >= 0.3:
                return parsed, errors
        except Exception as exc:  # pylint: disable=broad-except
            errors.append(f"Dateutil parsing error: {exc}")

        try:
            parsed = self._extract_dates_with_regex(series)
            if not parsed.isna().all():
                return parsed, errors
        except Exception as exc:  # pylint: disable=broad-except
            errors.append(f"Regex extraction error: {exc}")

        errors.append("Could not parse datetime column with any method")
        return pd.Series([pd.NaT] * len(series), index=series.index), errors

    @staticmethod
    def _extract_dates_with_regex(series: pd.Series) -> pd.Series:
        date_pattern = re.compile(r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}")
        extracted: List[pd.Timestamp | pd.NaT] = []
        for val in series:
            if pd.isna(val):
                extracted.append(pd.NaT)
                continue
            match = date_pattern.search(str(val))
            if match:
                try:
                    parsed_date = date_parser.parse(match.group())
                    extracted.append(parsed_date)
                except Exception:  # pylint: disable=broad-except
                    extracted.append(pd.NaT)
            else:
                extracted.append(pd.NaT)
        return pd.Series(extracted, index=series.index)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate_datetime_column(self, series: pd.Series) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "is_valid": True,
            "total_values": len(series),
            "parsed_values": 0,
            "missing_values": 0,
            "date_range": None,
            "frequency_hint": None,
            "issues": [],
        }
        result["missing_values"] = series.isna().sum()
        result["parsed_values"] = len(series) - result["missing_values"]
        if result["parsed_values"] == 0:
            result["is_valid"] = False
            result["issues"].append("No values could be parsed as datetime")
            return result
        valid_dates = series.dropna()
        if not valid_dates.empty:
            result["date_range"] = {
                "start": valid_dates.min(),
                "end": valid_dates.max(),
                "span_days": (valid_dates.max() - valid_dates.min()).days,
            }
        if len(valid_dates) > 2:
            try:
                sorted_dates = valid_dates.sort_values()
                time_diffs = sorted_dates.diff().dropna()
                mode_diff = time_diffs.mode()
                if not mode_diff.empty:
                    diff_days = mode_diff.iloc[0].days
                    diff_seconds = mode_diff.iloc[0].total_seconds()
                    if diff_days >= 365:
                        result["frequency_hint"] = "Yearly"
                    elif diff_days >= 28:
                        result["frequency_hint"] = "Monthly"
                    elif diff_days >= 7:
                        result["frequency_hint"] = "Weekly"
                    elif diff_days >= 1:
                        result["frequency_hint"] = "Daily"
                    elif diff_seconds >= 3600:
                        result["frequency_hint"] = "Hourly"
                    elif diff_seconds >= 60:
                        result["frequency_hint"] = "Per minute"
                    else:
                        result["frequency_hint"] = "High frequency"
            except Exception:  # pylint: disable=broad-except
                result["frequency_hint"] = "Irregular"
        if result["missing_values"] / result["total_values"] > 0.5:
            result["issues"].append(
                f"High number of missing values ({result['missing_values']}/{result['total_values']})"
            )
        if result.get("date_range") and result["date_range"]["span_days"] > 36500:
            result["issues"].append("Date range spans more than 100 years - check for parsing errors")
        return result

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------
    @staticmethod
    def filter_by_date_range(
        df: pd.DataFrame,
        date_column: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        filtered = df.copy()
        if start_date is not None:
            filtered = filtered[filtered[date_column] >= start_date]
        if end_date is not None:
            filtered = filtered[filtered[date_column] <= end_date]
        return filtered
