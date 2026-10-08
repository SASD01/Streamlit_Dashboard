import streamlit as st

from streamlit01.web.guard import require_page_permission

require_page_permission("fuels_dashboard")

st.title("Combustibles")
st.info("Dashboard de Combustibles en construcción.")