"""📁 Data Upload & Management page for Graph Anything Over Time.

This file is auto-generated from the original monolithic ``app.py``. It keeps the
exact same functionality but in the Streamlit multi-page format. Import order
and logic preserved.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Internal utilities
from utils.session_init import ensure_session_state

# Ensure common objects exist
ensure_session_state()

# Convenience aliases
fh = st.session_state.file_handler

# -----------------------------------------------------------------------------
# Page UI
# -----------------------------------------------------------------------------

st.markdown('<h2 class="subheader">📁 Data Upload & Management</h2>', unsafe_allow_html=True)

# File upload section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Upload Your Data Files")
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["csv", "xlsx", "xls", "json", "tsv"],
        accept_multiple_files=True,
        help="Supported formats: CSV, Excel (.xlsx, .xls), JSON, TSV",
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Validate file
            is_valid, error_message = fh.validate_file(uploaded_file)

            if is_valid:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    df, error = fh.read_file(uploaded_file)

                    if df is not None:
                        file_key = uploaded_file.name
                        fh.add_dataset(
                            file_key,
                            df,
                            {
                                "filename": uploaded_file.name,
                                "size": uploaded_file.size,
                                "upload_time": datetime.now(),
                                "type": uploaded_file.type,
                            },
                        )
                        st.success(f"✅ Successfully loaded {uploaded_file.name}")
                    else:
                        st.error(f"❌ Error loading {uploaded_file.name}: {error}")
            else:
                st.error(f"❌ {uploaded_file.name}: {error_message}")

with col2:
    st.markdown("### Quick Stats")
    datasets = fh.get_all_datasets()

    if datasets:
        st.metric("Datasets Loaded", len(datasets))
        total_rows = sum(len(df) for df in datasets.values())
        st.metric("Total Rows", f"{total_rows:,}")
        total_memory = (
            sum(df.memory_usage(deep=True).sum() for df in datasets.values())
            / (1024 * 1024)
        )
        st.metric("Memory Usage", f"{total_memory:.1f} MB")
    else:
        st.info("No datasets loaded yet")

# Display loaded datasets
if fh.get_dataset_names():
    st.markdown("### 📋 Loaded Datasets")

    for dataset_name in fh.get_dataset_names():
        with st.expander(f"📄 {dataset_name}", expanded=False):
            col1, col2, col3 = st.columns([3, 1, 1])

            df = fh.get_dataset(dataset_name)
            stats = fh.get_dataset_stats(dataset_name)

            with col1:
                st.write("**Preview:**")
                st.dataframe(df.head(), use_container_width=True)
                st.write("**Statistics:**")
                st.write(f"• **Rows:** {stats['rows']:,}")
                st.write(f"• **Columns:** {stats['columns']}")
                st.write(f"• **Numeric Columns:** {stats['numeric_columns']}")
                st.write(f"• **Text Columns:** {stats['text_columns']}")
                st.write(f"• **Missing Values:** {stats['missing_values']:,}")

            with col2:
                st.write("**Actions:**")
                if st.button("🔍 Analyze Dates", key=f"analyze_{dataset_name}"):
                    from pages.utils_date_analysis import analyze_datetime_columns  # lazily import helper
                    analyze_datetime_columns(dataset_name)

            with col3:
                st.write("**Remove:**")
                if st.button("🗑️ Delete", key=f"delete_{dataset_name}"):
                    fh.remove_dataset(dataset_name)
                    st.rerun()

# Sample data option
st.markdown("### 🎯 Try with Sample Data")
if st.button("Load Sample Time Series Data"):
    dates = pd.date_range(start="2020-01-01", end="2023-12-31", freq="D")
    np.random.seed(42)
    sample_data = pd.DataFrame(
        {
            "Date": dates,
            "Temperature": 20
            + 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
            + np.random.normal(0, 2, len(dates)),
            "Humidity": 50
            + 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 365 + np.pi / 4)
            + np.random.normal(0, 5, len(dates)),
            "Pressure": 1013
            + 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365 + np.pi / 2)
            + np.random.normal(0, 3, len(dates)),
            "Sales": np.maximum(
                0,
                1000
                + 500 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
                + np.random.normal(0, 100, len(dates)),
            ),
        }
    )

    fh.add_dataset(
        "Sample Weather & Sales Data",
        sample_data,
        {
            "filename": "sample_data.csv",
            "size": len(sample_data) * len(sample_data.columns) * 8,
            "upload_time": datetime.now(),
            "type": "sample",
        },
    )

    st.success("✅ Sample data loaded successfully!")
    st.rerun()
