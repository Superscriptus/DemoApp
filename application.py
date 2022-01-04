import streamlit as st
import streamlit_analytics
from streamlit import secrets

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

        if 'comparison_data' not in st.session_state:
            st.session_state.presets_loaded = False
            st.session_state.comparison_data = {
                preset: {
                    rep: {}
                    for rep in range(st.session_state.config.config_params['max_replicates'])
                }
                for preset in st.session_state.config.simulation_presets.keys()
            }

        st.sidebar.image('images/logo.png', use_column_width=True)
        st.sidebar.header('Simulation engine for a social teamwork game.')

        with streamlit_analytics.track(
            unsafe_password=secrets["ANALYTICS_PASSWORD"],
            firestore_key_file=secrets["FIRESTORE_KEY_FILE"],
            firestore_collection_name=secrets["FIRESTORE_COLLECTION"]
        ):

            if st.session_state.presets_loaded:
                selected_page = st.sidebar.selectbox(
                    label="App Navigation",
                    options=[*self.pages.keys()],
                    help="Select page to view.",
                    key="nav1",
                    index=0
                )
            else:
                selected_page = "About"
                st.sidebar.markdown("_Please wait while we load the simulations in the background._")

        create_session_state_variables()
        set_default_parameters()
        self.pages[selected_page].page_code()

        if not st.session_state.presets_loaded:

            for preset, parameters in st.session_state.config.simulation_presets.items():

                preset_e_flag = True if preset == 'E' else False
                parameter_dict = parameters

                for rep in range(st.session_state.config.config_params['max_replicates']):

                    st.session_state.comparison_data[preset][rep] = load_models(
                        project_count=parameter_dict['project_count'],
                        dept_workload=parameter_dict['dept_workload'],
                        budget_func=parameter_dict['budget_func'],
                        train_load=parameter_dict['train_load'],
                        skill_decay=parameter_dict['skill_decay'],
                        rep=rep,
                        team_allocation=parameter_dict['team_allocation'],
                        preset_e=preset_e_flag
                    )

            st.session_state.simulation_data = st.session_state.comparison_data['A'][st.session_state.replicate]
            st.session_state.presets_loaded = True
            st.experimental_rerun()
