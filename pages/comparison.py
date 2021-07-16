import streamlit as st


def page_code():

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