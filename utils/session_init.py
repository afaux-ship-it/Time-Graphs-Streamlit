"""Session initializer for Graph Anything Over Time.

Guarantees that all required objects live in Streamlit `st.session_state` so
individual page scripts can rely on them without boiler-plate duplication.
"""

from __future__ import annotations

import streamlit as st

# Local imports
from utils.file_handler import FileHandler
from utils.data_parser import DateTimeParser
from utils.plot_generator import PlotGenerator

__all__ = ["ensure_session_state"]


def ensure_session_state() -> None:
    """Populate missing keys in ``st.session_state``.

    This helper should be imported and called at the very top of every page
    module (including the landing ``app.py``). It is idempotent and inexpensive.
    """

    if "file_handler" not in st.session_state:
        st.session_state.file_handler = FileHandler()

    if "datetime_parser" not in st.session_state:
        st.session_state.datetime_parser = DateTimeParser()

    if "plot_generator" not in st.session_state:
        st.session_state.plot_generator = PlotGenerator()

    # Shared mutable containers for datasets
    st.session_state.setdefault("current_datasets", {})
    st.session_state.setdefault("parsed_datasets", {})
