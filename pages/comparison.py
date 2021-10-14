"""
TODO:
- refactor timeseries plot (use class from simulation?)
-
"""
import pandas as pd
import streamlit as st
import numpy as np
import altair as alt


def page_code():

    comparison_data = {}

    domain = list(st.session_state.config.simulation_presets.keys())
    colours = ['blue', 'orange', 'green', 'red']

    st.title("Comparison")

    st.write("Here we compare the performance of the model when simulated using the "
             "following parameter presets:")

    for preset, preset_details in st.session_state.config.simulation_presets.items():
        with st.beta_expander(preset + ": " + preset_details['preset_name']):
            st.write(preset_details['blurb'])

    chart_data = None
    for preset in st.session_state.config.simulation_presets:

        if chart_data is None:
            chart_data = (
                st.session_state.comparison_data[preset]['model_vars'][['time', 'Roi']]
                .copy().rename(columns={'Roi': 'value'})
            )
            chart_data['variable'] = [preset for i in range(len(chart_data))]

        else:
            temp_data = (
                st.session_state.comparison_data[preset]['model_vars'][['time', 'Roi']]
                .copy().rename(columns={'Roi': 'value'})
            )
            temp_data['variable'] = [preset for i in range(len(temp_data))]
            chart_data = chart_data.append(temp_data)

    _x = alt.X('time', axis=alt.Axis(title='timestep'))

    chart = alt.Chart(chart_data).mark_line().encode(
        x=_x,
        y=alt.Y('value', axis=alt.Axis(title='ROI')),
        color=alt.Color(
            'variable', scale=alt.Scale(
                domain=domain,
                range=colours
            )
        ),
    ).properties(title="ROI Comparison")

    st.altair_chart(chart, use_container_width=True)

    st.subheader("Bar chart test:")

    bar_data = pd.DataFrame({
        'preset': domain,
        'terminal ROI': [
            np.mean(st.session_state.comparison_data[preset]['model_vars'].loc[-25:]['Roi'])
            for preset in domain
        ]
    })
    bar_chart = alt.Chart(bar_data).mark_bar().encode(
        x='preset',
        y='terminal ROI',
        color=alt.Color(
            'preset', scale=alt.Scale(
                domain=domain,
                range=colours
            )
        )
    ).properties(title="Mean ROI over final 25 timesteps")
    st.altair_chart(bar_chart, use_container_width=True)
    #
    # st.bar_chart(bar_data)

