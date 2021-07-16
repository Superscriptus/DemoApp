import streamlit as st


def page_code():
    st.title("Testing Initial Hypotheses")
    st.markdown("This page will display plots for testing initial hypotheses...")

    st.sidebar.slider(
            "Select parameter value:",
            min_value=0,
            max_value=100,
            value=50,
        )

    option = st.selectbox(
            'Select hypothesis to view:',
            ('a) High risk projects (high stake) attract talent (high OVR)',
             'b) Cognitively diverse teams have higher success rate than randomly selected teams',
             'c) Superstars emerge',
             'd) Timeline flexibility pays off',
             '...'
             )
        )
    st.write('To display:', option)
