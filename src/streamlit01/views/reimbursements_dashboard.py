import streamlit as st

from streamlit01.web.guard import require_page_permission

require_page_permission("reimbursements_dashboard")

st.title("Reembolsos")
st.info("Dashboard de Reembolsos en construcción.")