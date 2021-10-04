import streamlit as st

from .simulation import load_data, set_default_parameters


def page_code():

    st.title("Comparison")

    st.write("This tab will allow comparison between two selected simulations.")
    option = st.multiselect(
        'Select team allocators:',
        ('Random',
         'Basic',
         'Niter0',
         'Basin',
         'Basin_w_flex'
         )
    )
    color = st.select_slider(
        'Select skill decay value:',
        options=[0.95, 0.99, 0.995]
    )
    st.image('images/projects_timeline_flex.png')
    st.write(st.session_state.data.head())
