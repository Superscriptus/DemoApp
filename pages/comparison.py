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

    st.write("Here we compare the presets...(more details to follow).")

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
        preset: [
            np.mean(st.session_state.comparison_data[preset]['model_vars'].loc[-25:]['Roi'])
            if d == preset
            else 0
            for d in domain
        ]
        for preset in domain
    }, index=domain)

    st.bar_chart(bar_data)

