"""Helper utilities shared across Streamlit pages – date-column analysis."""
from __future__ import annotations

import streamlit as st

from utils.session_init import ensure_session_state

ensure_session_state()


def analyze_datetime_columns(dataset_name: str) -> None:
    """Run DateTimeParser detection on a dataset and display results inline.

    This was originally part of the monolithic script; it is now a reusable
    helper so multiple pages can invoke it (e.g., Data-Upload page’s quick
    button).
    """

    df = st.session_state.file_handler.get_dataset(dataset_name)

    if df is not None:
        with st.spinner("Analyzing date/time columns..."):
            datetime_candidates = st.session_state.datetime_parser.detect_datetime_columns(df)

            if datetime_candidates:
                st.success(f"Found {len(datetime_candidates)} potential date/time columns:")

                for candidate in datetime_candidates:
                    confidence_color = (
                        "🟢" if candidate["confidence"] > 0.7 else "🟡" if candidate["confidence"] > 0.4 else "🔴"
                    )
                    st.write(
                        f"{confidence_color} **{candidate['column']}** (Confidence: {candidate['confidence']:.2f})"
                    )
                    st.write(f"   Format: {candidate['format_hint']}")
                    st.write(f"   Sample: {candidate['sample_values']}")
                    st.write("---")
            else:
                st.warning("No clear date/time columns detected. You may need to specify manually.")
