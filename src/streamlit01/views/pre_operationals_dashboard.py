import streamlit as st

from streamlit01.web.guard import require_page_permission

require_page_permission("pre_operationals_dashboard")

st.title("Preoperacionales")
st.info("Dashboard de Preoperacionales en construcción.")