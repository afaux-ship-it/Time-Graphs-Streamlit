"""📊 Create Visualizations page extracted from the original monolithic app.

Generates interactive Plotly charts from datasets with parsed time columns.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional

import streamlit as st
import pandas as pd
import numpy as np

from utils.session_init import ensure_session_state

# Make sure shared objects exist
ensure_session_state()

pg: "PlotGenerator" = st.session_state.plot_generator  # type: ignore
fh = st.session_state.file_handler

# -----------------------------------------------------------------------------
# Page UI
# -----------------------------------------------------------------------------

st.markdown('<h2 class="subheader">📊 Create Visualizations</h2>', unsafe_allow_html=True)

# Guard: need datasets with parsed time columns
if not st.session_state.parsed_datasets:
    st.warning("⚠️ No datasets with parsed time columns available. Please set up time columns first.")
    st.stop()

# Dataset selection
selected_dataset = st.selectbox("Select dataset for visualization:", list(st.session_state.parsed_datasets.keys()))
if not selected_dataset:
    st.stop()

dataset_info = st.session_state.parsed_datasets[selected_dataset]
df: pd.DataFrame = dataset_info["data"]
time_column: str = dataset_info["time_column"]

# Variable selection – only numeric cols (excluding time col)
numeric_columns: List[str] = df.select_dtypes(include=[np.number]).columns.tolist()
if time_column in numeric_columns:
    numeric_columns.remove(time_column)

if not numeric_columns:
    st.error("❌ No numeric columns available for plotting.")
    st.stop()

st.markdown("### 📈 Chart Configuration")
col1, col2 = st.columns([2, 1])

with col1:
    selected_variables = st.multiselect(
        "Select variables to plot:",
        options=numeric_columns,
        default=numeric_columns[:3] if len(numeric_columns) >= 3 else numeric_columns,
    )

    chart_type = st.selectbox(
        "Select chart type:",
        options=["Line Chart", "Scatter Plot", "Area Chart", "Bar Chart", "Box Plot"],
    )

with col2:
    st.markdown("**Quick Settings:**")
    color_palette = st.selectbox("Color palette:", options=list(pg.COLOR_PALETTES.keys()))
    show_markers = st.checkbox("Show markers", value=True)
    show_grid = st.checkbox("Show grid", value=True)
    width = st.slider("Width", 400, 1200, 800, 50)
    height = st.slider("Height", 300, 800, 500, 25)

# Generate plot if variables selected
if selected_variables:
    config: Dict[str, Any] = {
        "title": f"{', '.join(selected_variables)} Over Time",
        "width": width,
        "height": height,
        "color_palette": color_palette,
        "show_markers": show_markers,
        "show_grid": show_grid,
    }

    try:
        if chart_type == "Line Chart":
            fig = pg.create_line_chart(df, time_column, selected_variables, config)
        elif chart_type == "Scatter Plot":
            fig = pg.create_scatter_plot(df, time_column, selected_variables, config)
        elif chart_type == "Area Chart":
            fig = pg.create_area_chart(df, time_column, selected_variables, config)
        elif chart_type == "Bar Chart":
            fig = pg.create_bar_chart(df, time_column, selected_variables, config)
        elif chart_type == "Box Plot":
            fig = pg.create_box_plot(df, time_column, selected_variables, config)
        else:
            st.error("Unsupported chart type")
            st.stop()

        # Display
        st.plotly_chart(fig, use_container_width=True)

        # Export
        st.markdown("### 💾 Export Options")
        ec1, ec2 = st.columns(2)
        with ec1:
            if st.button("📊 Export PNG"):
                try:
                    img_bytes = fig.to_image(format="png", width=1200, height=800, scale=2)
                    st.download_button(
                        "Download PNG",
                        data=img_bytes,
                        file_name=f"{selected_dataset}_{chart_type.replace(' ', '_')}.png",
                        mime="image/png",
                    )
                except Exception as e:
                    st.error(f"Export failed: {e}")
        with ec2:
            if st.button("📊 Export HTML"):
                html_bytes = fig.to_html(include_plotlyjs=True).encode()
                st.download_button(
                    "Download HTML",
                    data=html_bytes,
                    file_name=f"{selected_dataset}_{chart_type.replace(' ', '_')}.html",
                    mime="text/html",
                )

    except Exception as e:
        st.error(f"❌ Error generating plot: {e}")
