"""
TODO:
- refactor timeseries plot (use class from simulation?)
- add other time series plots requested
- add OVR and success plots
- fix error message (no data on comparison page for pps 10)
"""
import pandas as pd
import streamlit as st
import numpy as np
import altair as alt

from .utilities import load_models
from .simulation import set_default_parameters


def time_series_plot(domain, colours, title):

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
    ).properties(title=title)

    st.altair_chart(chart, use_container_width=True)


def bar_chart_wrapper(element, bar_data, x, y, title, domain, colours,
                      colour_var, use_container_width=True, column=None):

    if column is not None:
        bar_chart = alt.Chart(bar_data).mark_bar().encode(
            x=x,
            y=y,
            color=alt.Color(
                colour_var, scale=alt.Scale(
                    domain=domain,
                    range=colours
                )
            ),
            column=column
        ).properties(title=title).configure_legend(orient='bottom')
    else:
        bar_chart = alt.Chart(bar_data).mark_bar().encode(
            x=x,
            y=y,
            color=alt.Color(
                colour_var, scale=alt.Scale(
                    domain=domain,
                    range=colours
                )
            )
        ).properties(title=title).configure_legend(orient='bottom')

    element.altair_chart(bar_chart, use_container_width=use_container_width)


def page_code():

    set_default_parameters()
    comparison_data = {}

    domain = list(st.session_state.config.simulation_presets.keys())
    colours = ['blue', 'orange', 'green', 'red']

    st.title("Comparison")

    st.write("Here we compare the performance of the model when simulated using the "
             "following parameter presets:")

    for preset, preset_details in st.session_state.config.simulation_presets.items():
        with st.beta_expander(preset + ": " + preset_details['preset_name']):
            st.write(preset_details['blurb'])

    time_series_plot(domain, colours, "ROI Comparison")

    col1, col2 = st.beta_columns([1, 1])
    col1.subheader("Bar chart test:")

    bar_data = pd.DataFrame({
        'preset': domain,
        'terminal ROI': [
            np.mean(st.session_state.comparison_data[preset]['model_vars'].loc[-25:]['Roi'])
            for preset in domain
        ]
    })
    bar_chart_wrapper(
        col1, bar_data, x='preset', y='terminal ROI',
        title="Mean ROI over final 25 timesteps",
        domain=domain, colours=colours,
        colour_var='preset',
        use_container_width=True, column=None
    )

    col2.subheader("Bar chart test 4:")

    load_types = ['ProjectLoad', 'Slack', 'TrainingLoad', 'DeptLoad']

    bar_data = pd.DataFrame()
    bar_data['preset'] = [p for p in domain for s in load_types]
    bar_data['Load Type'] = [s for s in load_types] * len(domain)

    load_column = []
    for preset, parameters in st.session_state.config.simulation_presets.items():
        parameter_dict = parameters

        for lt in load_types:
            load_column.append(
                np.mean(st.session_state.comparison_data[preset]['model_vars'].loc[-25:][lt])
            )

    bar_data['Load'] = load_column

    bar_chart_wrapper(
        col2, bar_data, x='preset', y='Load',
        title="Mean Load over final 25 timesteps",
        domain=load_types, colours=colours,
        colour_var='Load Type',
        use_container_width=True, column=None
    )

    col3, col4 = st.beta_columns([1, 1])
    col3.subheader("Comparing skill decays:")

    all_skill_decays = [0.95, 0.99, 0.995]
    all_skill_decay_data = {}

    bar_data = pd.DataFrame()
    bar_data['preset'] = [p for p in domain for s in all_skill_decays]
    bar_data['skill_decay'] = [s for s in all_skill_decays] * len(domain)

    terminal_roi_column = []
    for preset, parameters in st.session_state.config.simulation_presets.items():
        parameter_dict = parameters

        for skill_decay in all_skill_decays:

            all_skill_decay_data[(preset, skill_decay)] = load_models(
                project_count=parameter_dict['project_count'],
                dept_workload=parameter_dict['dept_workload'],
                budget_func=parameter_dict['budget_func'],
                train_load=parameter_dict['train_load'],
                skill_decay=skill_decay,
                rep=st.session_state.replicate,
                team_allocation=parameter_dict['team_allocation'],
                load_networks=False
            )
            terminal_roi_column.append(
                np.mean(all_skill_decay_data[(preset, skill_decay)]['model_vars'].loc[-25:]['Roi'])
                if all_skill_decay_data[(preset, skill_decay)]['model_vars'] is not None
                else None
            )
    bar_data['terminal ROI'] = terminal_roi_column

    bar_chart_wrapper(
        col3, bar_data, x='skill_decay:N', y='terminal ROI',
        title="Mean ROI over final 25 timesteps",
        domain=domain, colours=colours,
        colour_var='preset',
        use_container_width=False, column='preset'
    )

    col4.subheader("Comparing training loads:")

    all_train_loads = [0.0, 0.1, 0.3, 2.0]
    all_train_load_data = {}

    bar_data = pd.DataFrame()
    bar_data['preset'] = [p for p in domain for s in all_train_loads]
    bar_data['train_load'] = [s if s != 2.0 else 'boost' for s in all_train_loads] * len(domain)

    terminal_roi_column = []
    for preset, parameters in st.session_state.config.simulation_presets.items():
        parameter_dict = parameters

        for train_load in all_train_loads:

            all_train_load_data[(preset, train_load)] = load_models(
                project_count=parameter_dict['project_count'],
                dept_workload=parameter_dict['dept_workload'],
                budget_func=parameter_dict['budget_func'],
                train_load=train_load,
                skill_decay=parameter_dict['skill_decay'],
                rep=st.session_state.replicate,
                team_allocation=parameter_dict['team_allocation'],
                load_networks=False
            )
            terminal_roi_column.append(
                np.mean(all_train_load_data[(preset, train_load)]['model_vars'].loc[-25:]['Roi'])
                if all_train_load_data[(preset, train_load)]['model_vars'] is not None
                else None
            )
    bar_data['terminal ROI'] = terminal_roi_column

    bar_chart_wrapper(
        col4, bar_data, x='train_load:N', y='terminal ROI',
        title="Mean ROI over final 25 timesteps",
        domain=domain, colours=colours,
        colour_var='preset',
        use_container_width=False, column='preset'
    )





