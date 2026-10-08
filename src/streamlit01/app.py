import streamlit as st

from streamlit01.web.authenticator import handle_authentication
from streamlit01.web.navigation import render_navigation
from streamlit01.web.session_manager import (
    init_session_state,
    is_authenticated,
)

st.set_page_config(
    page_title="Portal Logistic",
    page_icon="🚚",
    layout="wide",
)

init_session_state()
handle_authentication()

if not is_authenticated():
    st.stop()

render_navigation()