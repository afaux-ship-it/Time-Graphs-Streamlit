"""⚙️ Advanced Settings page – data management utilities."""

from __future__ import annotations

import streamlit as st

from utils.session_init import ensure_session_state

ensure_session_state()

fh = st.session_state.file_handler

st.markdown('<h2 class="subheader">⚙️ Advanced Settings</h2>', unsafe_allow_html=True)

st.markdown("🔧 Data Management")

c1, c2 = st.columns(2)

with c1:
    if st.button("🗑️ Clear All Datasets"):
        fh.clear_all_datasets()
        st.session_state.parsed_datasets.clear()
        st.success("✅ All datasets cleared!")
        st.rerun()

with c2:
    if st.button("🔄 Reset Application"):
        for key in list(st.session_state.keys()):
            if key not in ["file_handler", "datetime_parser", "plot_generator"]:
                del st.session_state[key]
        st.success("✅ Application reset!")
        st.rerun()
