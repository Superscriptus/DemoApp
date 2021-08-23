import streamlit as st


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
