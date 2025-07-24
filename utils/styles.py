"""Shared style utilities for the Graph Anything Over Time app."""

from __future__ import annotations

import streamlit as st

_GLOBAL_CSS = """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subheader {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        background-color: #f8d7da;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        background-color: #d4edda;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
"""

def inject_global_css() -> None:
    """Inject the shared CSS into the current Streamlit page only once."""
    if _GLOBAL_CSS not in st.session_state.get("_injected_css", set()):
        st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
        injected = st.session_state.get("_injected_css", set())
        injected.add(_GLOBAL_CSS)
        st.session_state._injected_css = injected
