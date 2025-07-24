"""Session initializer for Graph Anything Over Time.

Guarantees that all required objects live in Streamlit `st.session_state` so
individual page scripts can rely on them without boiler-plate duplication.
"""

from __future__ import annotations

import streamlit as st

# Local imports
from utils.file_handler import FileHandler
from utils import datetime as dt_mod
from utils import plot as plot_mod

__all__ = ["ensure_session_state"]


def _hide_unwanted_pages() -> None:
    """Remove unnecessary pages from Streamlit navigation sidebar.

    This relies on the *experimental* ``st.experimental_get_pages`` API that
    returns the internal page registry as a ``dict``.  By deleting keys from
    this mapping **before** the first widget is rendered, the corresponding
    entries disappear from the sidebar navigation.
    """

    try:
        import streamlit as _st  # local import to avoid polluting public namespace

        pages = _st.experimental_get_pages()  # type: ignore[attr-defined]
        for key, page in list(pages.items()):
            if (
                page.get("page_name") in {"App", "Utils Date Analysis"}
                or page.get("module") in {"app", "pages.utils_date_analysis"}
                or page.get("module", "").endswith("app")
                or page.get("module", "").endswith("utils_date_analysis")
            ):
                del pages[key]
    except Exception:
        # Fail silently if Streamlit version does not expose the helper
        # _or_ if its internals change in the future. The worst-case outcome
        # is that the redundant pages remain visible, which is acceptable.
        pass


def ensure_session_state() -> None:
    """Populate missing objects in ``st.session_state`` and clean sidebar."""

    # Remove navigation entries that the product does not expose to end users
    _hide_unwanted_pages()



    if "file_handler" not in st.session_state:
        st.session_state.file_handler = FileHandler()

    if "datetime_parser" not in st.session_state:
        # keep backward compat: store original parser instance
        st.session_state.datetime_parser = dt_mod.DateParser()._impl  # type: ignore

    if "datetime" not in st.session_state:
        st.session_state.datetime = dt_mod

    if "plot_generator" not in st.session_state:
        # store the lightweight plot module; pages treat it like an API surface
        st.session_state.plot_generator = plot_mod

    # Shared mutable containers for datasets
    st.session_state.setdefault("current_datasets", {})
    st.session_state.setdefault("parsed_datasets", {})
