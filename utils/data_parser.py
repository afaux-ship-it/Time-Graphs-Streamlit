"""
Date/time parsing utilities for Graph Anything Over Time application.
Handles intelligent detection and parsing of various date/time formats.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from dateutil import parser as date_parser
import pytz
import re
from typing import List, Dict, Tuple, Optional, Any
import streamlit as st
import config


class DateTimeParser:
    """Handles detection and parsing of date/time columns."""
    
    # Common date patterns for format detection
    DATE_PATTERNS = config.DATE_PATTERNS  # type: ignore
    # The literal list is now stored in config.py
    # Keeping this attribute for backward compatibility

    # Common datetime formats to try
    DATETIME_FORMATS = config.DATETIME_FORMATS  # type: ignore
    # Refer to config for actual formats

    def __init__(self):
        """Initialize DateTimeParser."""
        self.timezone = pytz.UTC
    
    def detect_datetime_columns(self, df: pd.DataFrame, 
                              sample_size: int = 100) -> List[Dict[str, Any]]:
        """
        Detect potential datetime columns in a DataFrame.
        
        Args:
            df: Pandas DataFrame to analyze
            sample_size: Number of rows to sample for detection
            
        Returns:
            List of dictionaries with column info and confidence scores
        """
        datetime_candidates = []
        
        # Sample data for faster processing
        sample_df = df.head(sample_size) if len(df) > sample_size else df
        
        for column in df.columns:
            if df[column].dtype == 'object' or pd.api.types.is_string_dtype(df[column]):
                confidence, format_hint = self._analyze_column_for_datetime(
                    sample_df[column].dropna()
                )
                
                if confidence > 0.3:  # Threshold for considering as datetime
                    datetime_candidates.append({
                        'column': column,
                        'confidence': confidence,
                        'format_hint': format_hint,
                        'sample_values': sample_df[column].dropna().head(3).tolist()
                    })
            
            elif pd.api.types.is_numeric_dtype(df[column]):
                # Check for Unix timestamps
                confidence, format_hint = self._check_unix_timestamp(
                    sample_df[column].dropna()
                )
                
                if confidence > 0.5:
                    datetime_candidates.append({
                        'column': column,
                        'confidence': confidence,
                        'format_hint': format_hint,
                        'sample_values': sample_df[column].dropna().head(3).tolist()
                    })
        
        # Sort by confidence score
        datetime_candidates.sort(key=lambda x: x['confidence'], reverse=True)
        
        return datetime_candidates
    
    def _analyze_column_for_datetime(self, series: pd.Series) -> Tuple[float, str]:
        """
        Analyze a column for datetime patterns.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Tuple of (confidence_score, format_hint)
        """
        if len(series) == 0:
            return 0.0, "No data"
        
        total_values = len(series)
        parsed_count = 0
        format_matches = {}
        
        for value in series:
            if pd.isna(value):
                continue
                
            str_value = str(value).strip()
            
            # Try pattern matching first
            for pattern in self.DATE_PATTERNS:
                if re.match(pattern, str_value):
                    format_matches[pattern] = format_matches.get(pattern, 0) + 1
                    break
            
            # Try parsing with dateutil
            try:
                date_parser.parse(str_value)
                parsed_count += 1
            except (ValueError, TypeError, OverflowError):
                continue
        
        # Calculate confidence based on successful parsing
        confidence = parsed_count / total_values if total_values > 0 else 0
        
        # Determine most likely format
        if format_matches:
            best_pattern = max(format_matches, key=format_matches.get)
            format_hint = self._pattern_to_format_hint(best_pattern)
        else:
            format_hint = "Mixed or custom format"
        
        return confidence, format_hint
    
    def _check_unix_timestamp(self, series: pd.Series) -> Tuple[float, str]:
        """
        Check if numeric column contains Unix timestamps.
        
        Args:
            series: Numeric pandas Series
            
        Returns:
            Tuple of (confidence_score, format_hint)
        """
        if len(series) == 0:
            return 0.0, "No data"
        
        # Check if values are in reasonable timestamp range
        min_val = series.min()
        max_val = series.max()
        
        # Unix timestamp ranges (approximate)
        # Seconds: 1970-01-01 to 2038-01-19
        # Milliseconds: same range but * 1000
        
        timestamp_ranges = [
            (0, 2147483647, "Unix timestamp (seconds)"),  # 32-bit max
            (0, 2147483647000, "Unix timestamp (milliseconds)"),
            (315532800, 4102444800, "Unix timestamp (seconds, 1980-2100)"),  # More reasonable range
        ]
        
        confidence = 0.0
        format_hint = "Not a timestamp"
        
        for min_range, max_range, hint in timestamp_ranges:
            if min_range <= min_val <= max_range and min_range <= max_val <= max_range:
                # Check if conversion to datetime makes sense
                try:
                    if max_val > 2147483647:  # Likely milliseconds
                        test_date = pd.to_datetime(series.iloc[0], unit='ms')
                    else:  # Likely seconds
                        test_date = pd.to_datetime(series.iloc[0], unit='s')
                    
                    # Check if resulting date is reasonable (between 1970 and 2050)
                    if pd.Timestamp('1970-01-01') <= test_date <= pd.Timestamp('2050-01-01'):
                        confidence = 0.8
                        format_hint = hint
                        break
                        
                except (ValueError, OverflowError, pd.errors.OutOfBoundsDatetime):
                    continue
        
        return confidence, format_hint
    
    def _pattern_to_format_hint(self, pattern: str) -> str:
        """Convert regex pattern to human-readable format hint."""
        pattern_hints = {
            r'\d{4}-\d{2}-\d{2}': "YYYY-MM-DD",
            r'\d{2}/\d{2}/\d{4}': "MM/DD/YYYY or DD/MM/YYYY",
            r'\d{2}-\d{2}-\d{4}': "MM-DD-YYYY or DD-MM-YYYY",
            r'\d{1,2}/\d{1,2}/\d{4}': "M/D/YYYY",
            r'\d{1,2}-\d{1,2}-\d{4}': "M-D-YYYY",
            r'\d{4}/\d{2}/\d{2}': "YYYY/MM/DD",
            r'\d{4}\d{2}\d{2}': "YYYYMMDD"
        }
        return pattern_hints.get(pattern, "Custom format")
    
    def parse_datetime_column(self, series: pd.Series, 
                            format_hint: Optional[str] = None,
                            custom_format: Optional[str] = None) -> Tuple[pd.Series, List[str]]:
        """
        Parse a series as datetime.
        
        Args:
            series: Pandas Series to parse
            format_hint: Hint about the format
            custom_format: Custom strptime format string
            
        Returns:
            Tuple of (parsed_series, list_of_errors)
        """
        errors = []
        
        # If custom format is provided, try it first
        if custom_format:
            try:
                parsed = pd.to_datetime(series, format=custom_format, errors='coerce')
                if not parsed.isna().all():
                    return parsed, errors
                else:
                    errors.append(f"Custom format '{custom_format}' failed to parse any values")
            except Exception as e:
                errors.append(f"Custom format error: {str(e)}")
        
        # Check if it's a Unix timestamp
        if format_hint and "timestamp" in format_hint.lower():
            try:
                if "milliseconds" in format_hint.lower():
                    parsed = pd.to_datetime(series, unit='ms', errors='coerce')
                else:
                    parsed = pd.to_datetime(series, unit='s', errors='coerce')
                
                if not parsed.isna().all():
                    return parsed, errors
                    
            except Exception as e:
                errors.append(f"Timestamp parsing error: {str(e)}")
        
        # Try common formats
        for fmt in self.DATETIME_FORMATS:
            try:
                parsed = pd.to_datetime(series, format=fmt, errors='coerce')
                # Check if at least 50% of values were parsed successfully
                success_rate = (len(parsed) - parsed.isna().sum()) / len(parsed)
                if success_rate >= 0.5:
                    return parsed, errors
            except Exception:
                continue
        
        # Try with dateutil parser (more flexible but slower)
        try:
            parsed = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
            success_rate = (len(parsed) - parsed.isna().sum()) / len(parsed)
            if success_rate >= 0.3:
                return parsed, errors
        except Exception as e:
            errors.append(f"Dateutil parsing error: {str(e)}")
        
        # Last resort: try to extract dates with regex
        try:
            parsed = self._extract_dates_with_regex(series)
            if not parsed.isna().all():
                return parsed, errors
        except Exception as e:
            errors.append(f"Regex extraction error: {str(e)}")
        
        errors.append("Could not parse datetime column with any method")
        return pd.Series([pd.NaT] * len(series), index=series.index), errors
    
    def _extract_dates_with_regex(self, series: pd.Series) -> pd.Series:
        """Extract dates using regex patterns as last resort."""
        date_pattern = re.compile(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}')
        
        extracted_dates = []
        for value in series:
            if pd.isna(value):
                extracted_dates.append(pd.NaT)
                continue
                
            match = date_pattern.search(str(value))
            if match:
                try:
                    date_str = match.group()
                    parsed_date = date_parser.parse(date_str)
                    extracted_dates.append(parsed_date)
                except:
                    extracted_dates.append(pd.NaT)
            else:
                extracted_dates.append(pd.NaT)
        
        return pd.Series(extracted_dates, index=series.index)
    
    def validate_datetime_column(self, series: pd.Series) -> Dict[str, Any]:
        """
        Validate a parsed datetime column.
        
        Args:
            series: Parsed datetime Series
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'is_valid': True,
            'total_values': len(series),
            'parsed_values': 0,
            'missing_values': 0,
            'date_range': None,
            'frequency_hint': None,
            'issues': []
        }
        
        # Count parsed vs missing values
        result['missing_values'] = series.isna().sum()
        result['parsed_values'] = len(series) - result['missing_values']
        
        if result['parsed_values'] == 0:
            result['is_valid'] = False
            result['issues'].append("No values could be parsed as datetime")
            return result
        
        # Get date range
        valid_dates = series.dropna()
        if len(valid_dates) > 0:
            result['date_range'] = {
                'start': valid_dates.min(),
                'end': valid_dates.max(),
                'span_days': (valid_dates.max() - valid_dates.min()).days
            }
        
        # Try to infer frequency
        if len(valid_dates) > 2:
            try:
                # Sort dates and calculate differences
                sorted_dates = valid_dates.sort_values()
                time_diffs = sorted_dates.diff().dropna()
                
                # Find most common time difference
                mode_diff = time_diffs.mode()
                if len(mode_diff) > 0:
                    diff_days = mode_diff.iloc[0].days
                    diff_seconds = mode_diff.iloc[0].total_seconds()
                    
                    if diff_days >= 365:
                        result['frequency_hint'] = "Yearly"
                    elif diff_days >= 28:
                        result['frequency_hint'] = "Monthly"
                    elif diff_days >= 7:
                        result['frequency_hint'] = "Weekly"
                    elif diff_days >= 1:
                        result['frequency_hint'] = "Daily"
                    elif diff_seconds >= 3600:
                        result['frequency_hint'] = "Hourly"
                    elif diff_seconds >= 60:
                        result['frequency_hint'] = "Per minute"
                    else:
                        result['frequency_hint'] = "High frequency"
                        
            except Exception:
                result['frequency_hint'] = "Irregular"
        
        # Check for potential issues
        if result['missing_values'] / result['total_values'] > 0.5:
            result['issues'].append(f"High number of missing values ({result['missing_values']}/{result['total_values']})")
        
        if result['date_range'] and result['date_range']['span_days'] > 36500:  # > 100 years
            result['issues'].append("Date range spans more than 100 years - check for parsing errors")
        
        return result
    
    def filter_by_date_range(self, df: pd.DataFrame, 
                           date_column: str,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Filter DataFrame by date range.
        
        Args:
            df: DataFrame to filter
            date_column: Name of the datetime column
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        if start_date:
            filtered_df = filtered_df[filtered_df[date_column] >= start_date]
        
        if end_date:
            filtered_df = filtered_df[filtered_df[date_column] <= end_date]
        
        return filtered_df
