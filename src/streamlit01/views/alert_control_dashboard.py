import streamlit as st

from streamlit01.web.guard import require_page_permission

require_page_permission("alert_control_dashboard")

st.title("Alertas")
st.info("Dashboard de Alertas en construcción.")