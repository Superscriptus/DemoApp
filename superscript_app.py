# """
# TODO:
# - check if tabs works on Github sharing (find alternative option to show MC)
# - add requirements.txt and README.md (with instructions for MC)
# - check new github access and push
# - create notebook to generate static images
# - implement live plotting from data (create data aggregation/pre-processing)
# - read about secrets management
# - issues with layout and SVG display...
# """
#
# import streamlit as st
# # To make things easier later, we're also importing numpy and pandas for
# # working with sample data.
# import numpy as np
# import pandas as pd
#
# st.title('SuperScript Visualization')
#
# st.write("Here's our first attempt at using data to create a table:")
# st.write(pd.DataFrame({
#     'first column': [1, 2, 3, 4],
#     'second column': [10, 20, 30, 40]
# }))
#
import streamlit as st

col1, col2, col3 = st.beta_columns([1,5,1])

with col1:
    st.write("")
with col2:
    st.image('images/logo.png', use_column_width=True)#, width=400)
with col3:
    st.write("")

st.header('Simulation engine for a social teamwork game')

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)
query_params = st.experimental_get_query_params()
tabs = ["Simulation", "Comparison", "Hypotheses"]
if "tab" in query_params:
    active_tab = query_params["tab"][0]
else:
    active_tab = "Simulation"

if active_tab not in tabs:
    st.experimental_set_query_params(tab="Simulation")
    active_tab = "Simulation"

li_items = "".join(
    f"""
    <li class="nav-item">
        <a class="nav-link{' active' if t==active_tab else ''}" href="/?tab={t}">{t}</a>
    </li>
    """
    for t in tabs
)
tabs_html = f"""
    <ul class="nav nav-tabs">
    {li_items}
    </ul>
"""

st.markdown(tabs_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if active_tab == "Simulation":
    st.write("This tab will show animation of a simulation (approximately like running the Mesa server).")
    st.image("images/screenshot.png")
    # st.slider(
    #     "Note: value not preserved between tabs!",
    #     min_value=0,
    #     max_value=100,
    #     value=50,
    # )
elif active_tab == "Comparison":
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
elif active_tab == "Hypotheses":
    st.write("This tab will display plots for testing initial hypotheses.")
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
else:
    st.error("Error: tab not implemented.")
