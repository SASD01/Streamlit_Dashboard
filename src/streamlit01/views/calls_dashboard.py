import streamlit as st

from streamlit01.web.guard import require_page_permission

require_page_permission("calls_dashboard")

st.title("Llamadas")
st.info("Dashboard de Llamadas en construcción.")