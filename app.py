"""Graph Anything Over Time  root launcher

This minimal root script simply sets global configuration, injects shared CSS,
and shows the landing page. All functional pages now reside in the pages/
folder and shared helpers live in utils/.
"""

from __future__ import annotations

import streamlit as st
from utils.session_init import ensure_session_state
from utils.styles import inject_global_css

ensure_session_state()

st.set_page_config(
    page_title="Graph Anything Over Time",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()

def main() -> None:
    st.markdown(
        '<h1 class="main-header"> Graph Anything Over Time</h1>',
        unsafe_allow_html=True,
    )
    st.success("Use the sidebar to navigate through the app sections ")

if __name__ == "__main__":
    main()
