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

        st.sidebar.image('images/logo.png', use_column_width=True)
        selected_page = st.sidebar.selectbox(
            'App Navigation',
            [*self.pages.keys()]
        )

        self.pages[selected_page].page_code()
