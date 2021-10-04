import streamlit as st


def create_session_state_variables():

    if 'team_allocation' not in st.session_state:
        st.session_state.team_allocation = "Random"

    if 'replicate' not in st.session_state:
        st.session_state.replicate = 0

    if 'preset_active' not in st.session_state:
        st.session_state.preset_active = False

