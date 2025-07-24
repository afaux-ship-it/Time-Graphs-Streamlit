"""🕐 Time Column Setup page extracted from the original monolithic script."""

from __future__ import annotations

from typing import Optional, Any, Dict, List

import streamlit as st
import pandas as pd

from utils.session_init import ensure_session_state

ensure_session_state()

fh = st.session_state.file_handler
parser = st.session_state.datetime_parser

# -----------------------------------------------------------------------------
# Helper functions (ported from original app.py)
# -----------------------------------------------------------------------------

def parse_time_column(dataset_name: str, time_column: str, custom_format: Optional[str] = None) -> None:
    df = fh.get_dataset(dataset_name)
    if df is None:
        st.error("Dataset not found")
        return

    with st.spinner(f"Parsing time column '{time_column}'..."):
        parsed_series, errors = parser.parse_datetime_column(df[time_column], custom_format=custom_format)
        validation_results = parser.validate_datetime_column(parsed_series)

        st.session_state[f"parsed_time_{dataset_name}"] = {
            "column_name": time_column,
            "parsed_series": parsed_series,
            "validation": validation_results,
            "errors": errors,
        }

        df_updated = df.copy()
        df_updated[f"{time_column}_parsed"] = parsed_series
        st.session_state.parsed_datasets[dataset_name] = {
            "data": df_updated,
            "time_column": f"{time_column}_parsed",
            "original_time_column": time_column,
        }


def show_parsing_results(dataset_name: str, time_column: str) -> None:
    results = st.session_state[f"parsed_time_{dataset_name}"]
    validation = results["validation"]

    if validation["is_valid"]:
        st.success("✅ Time column parsed successfully!")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Values", validation["total_values"])
            st.metric("Parsed Values", validation["parsed_values"])
        with col2:
            st.metric("Missing Values", validation["missing_values"])
            success_rate = (validation["parsed_values"] / validation["total_values"]) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col3:
            if validation["date_range"]:
                st.metric("Date Range", f"{validation['date_range']['span_days']} days")
            if validation["frequency_hint"]:
                st.metric("Frequency", validation["frequency_hint"])
        if validation["date_range"]:
            st.write(
                f"**Date Range:** {validation['date_range']['start'].strftime('%Y-%m-%d')} to {validation['date_range']['end'].strftime('%Y-%m-%d')}"
            )
        if validation["issues"]:
            with st.expander("⚠️ Potential Issues"):
                for issue in validation["issues"]:
                    st.warning(issue)
    else:
        st.error("❌ Failed to parse time column")
        if results["errors"]:
            with st.expander("Error Details"):
                for error in results["errors"]:
                    st.error(error)


def manual_time_selection(dataset_name: str, df: pd.DataFrame) -> None:
    st.markdown("### 🔧 Manual Time Column Selection")
    col1, col2 = st.columns([1, 1])
    with col1:
        time_column = st.selectbox("Select time column:", options=df.columns.tolist())
        st.write("**Sample values:**")
        st.write(df[time_column].head().tolist())
    with col2:
        custom_format = st.text_input("Custom format (optional):", placeholder="%Y-%m-%d")
        if st.button("Parse Column"):
            parse_time_column(dataset_name, time_column, custom_format)

# -----------------------------------------------------------------------------
# Main Page UI
# -----------------------------------------------------------------------------

st.markdown('<h2 class="subheader">🕐 Time Column Setup</h2>', unsafe_allow_html=True)

datasets = fh.get_dataset_names()
if not datasets:
    st.warning("⚠️ No datasets loaded. Please upload data first.")
    st.stop()

selected_dataset = st.selectbox("Select dataset to configure:", datasets)
if not selected_dataset:
    st.stop()

df = fh.get_dataset(selected_dataset)

# Detection section
st.markdown("### 🔍 Automatic Date Detection")
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🚀 Auto-Detect Time Columns"):
        with st.spinner("Analyzing columns..."):
            datetime_candidates = parser.detect_datetime_columns(df)
            st.session_state[f"datetime_candidates_{selected_dataset}"] = datetime_candidates
with col2:
    if st.button("🔄 Refresh Analysis"):
        st.session_state.pop(f"datetime_candidates_{selected_dataset}", None)
        st.rerun()

candidates = st.session_state.get(f"datetime_candidates_{selected_dataset}")
if candidates is None:
    st.info("Click 'Auto-Detect Time Columns' to analyze your data.")
    st.stop()

if not candidates:
    st.warning("No potential time columns detected. You can manually select a column below.")
    manual_time_selection(selected_dataset, df)
    st.stop()

# Show detection results
st.markdown("### 📊 Detection Results")
best_candidate = candidates[0]
st.success(
    f"🎯 **Recommended Time Column:** `{best_candidate['column']}` (Confidence: {best_candidate['confidence']:.2f})"
)
with st.expander("View All Detected Columns"):
    for i, candidate in enumerate(candidates):
        confidence_icon = "🟢" if candidate["confidence"] > 0.7 else "🟡" if candidate["confidence"] > 0.4 else "🔴"
        st.write(f"{confidence_icon} **{candidate['column']}** - Confidence: {candidate['confidence']:.2f}")
        st.write(f"   Format: {candidate['format_hint']}")
        st.write(f"   Samples: {candidate['sample_values']}")
        if i < len(candidates) - 1:
            st.write("---")

# Configuration section
st.markdown("### ⚙️ Configure Time Column")
col1, col2 = st.columns([1, 1])
with col1:
    time_column = st.selectbox(
        "Select time column:", options=df.columns.tolist(), index=df.columns.tolist().index(best_candidate["column"])
    )
    use_custom_format = st.checkbox("Use custom date format")
    custom_format = None
    if use_custom_format:
        custom_format = st.text_input("Custom format (strptime):", placeholder="%Y-%m-%d")
with col2:
    if st.button("🔧 Parse Time Column", type="primary"):
        parse_time_column(selected_dataset, time_column, custom_format)

if f"parsed_time_{selected_dataset}" in st.session_state:
    show_parsing_results(selected_dataset, time_column)
