# """
# TODO:
# - check if tabs works on Github sharing (find alternative option to show MC)
# - add requirements.txt and README.md (with instructions for MC)
# - check new github access and push
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

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)
query_params = st.experimental_get_query_params()
tabs = ["Home", "About", "Contact"]
if "tab" in query_params:
    active_tab = query_params["tab"][0]
else:
    active_tab = "Home"

if active_tab not in tabs:
    st.experimental_set_query_params(tab="Home")
    active_tab = "Home"

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
    st.write("This tab will show animation of a simulation.")
    st.write("Example widget control:")
    st.slider(
        "Note: value not preserved between tabs!",
        min_value=0,
        max_value=100,
        value=50,
    )
elif active_tab == "Comparison":
    st.write("This tab will allow comparison between two selected simulations.")
elif active_tab == "Hypotheses":
    st.write("This tab will display plots for testing initial hypotheses.")
else:
    st.error("Error: tab not implemented.")
