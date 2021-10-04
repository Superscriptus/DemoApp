import streamlit as st

from pages.utilities import create_session_state_variables
from pages.simulation import load_data, set_default_parameters


class Application:

    def __init__(self):
        self.pages = {}

    def create_page(self, page_name, page):
        self.pages[page_name] = page

    def execute(self):
        """
        Function sets up the sidebar and adds dropdown for page select. Then runs the
        page_code for the selected page.
        """

        if 'config' not in st.session_state:
            from config import Config
            st.session_state.config = Config()

        create_session_state_variables()
        set_default_parameters()
        load_data(
            st.session_state.project_count,
            st.session_state.dept_workload,
            st.session_state.budget_func,
            st.session_state.skill_decay,
            st.session_state.train_load,
            st.session_state.replicate
        )

        st.sidebar.image('images/logo.png', use_column_width=True)
        st.sidebar.header('Simulation engine for a social teamwork game.')
        selected_page = st.sidebar.selectbox(
            'App Navigation',
            [*self.pages.keys()],
            help="Select page to view."
        )

        self.pages[selected_page].page_code()
