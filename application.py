import streamlit as st

from pages.utilities import create_session_state_variables
from pages.simulation import load_models, set_default_parameters


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

        st.sidebar.image('images/logo.png', use_column_width=True)
        st.sidebar.header('Simulation engine for a social teamwork game.')
        selected_page = st.sidebar.selectbox(
            'App Navigation',
            [*self.pages.keys()],
            help="Select page to view."
        )

        self.pages[selected_page].page_code()

        create_session_state_variables()
        set_default_parameters()
        st.session_state.comparison_data = {}

        for preset, parameters in st.session_state.config.simulation_presets.items():
            parameter_dict = parameters

            st.session_state.comparison_data[preset] = load_models(
                project_count=parameter_dict['project_count'],
                dept_workload=parameter_dict['dept_workload'],
                budget_func=parameter_dict['budget_func'],
                train_load=parameter_dict['train_load'],
                skill_decay=parameter_dict['skill_decay'],
                rep=st.session_state.replicate,
                team_allocation=parameter_dict['team_allocation']
            )

