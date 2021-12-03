"""
TODO:
- refactor timeseries plot (use class from simulation?)
- make grouped bar charts prettier: https://stackoverflow.com/questions/43797379/how-to-create-a-grouped-bar-chart-in-altair
- introduce replicates: run retrospective analysis, and random choice from available replicates (load all initially?)
- add preset E: new data files from agents_vars.pickle -> 'WorkersOnProjects',
       'WorkersWithoutProjects', 'WorkersOnTraining', 'AverageWorkerOvr', 'WorkerTurnover', 'ProjectLoad',
       'TrainingLoad', 'DeptLoad', 'Slack', 'ProjectsPerWorker', AND:
       IF SLACK ALREADY <10%, NO WORKERS REMOVED AND ALL METRICS UNCHANGED.
       OTHERWISE RANDOM SELECTION OF WORKERS REMOVED

       NEED TO CHECK: are load metrics computed UNIT-wise, or worker-wise? **************
"""
import pandas as pd
import streamlit as st
import numpy as np
import altair as alt

from .utilities import load_models, moving_average
from .simulation import set_default_parameters


def time_series_plot(chart_data, domain, colours, title, ylabel):

    _x = alt.X('time', axis=alt.Axis(title='timestep'))

    chart = alt.Chart(chart_data).mark_line().encode(
        x=_x,
        y=alt.Y('value', axis=alt.Axis(title=ylabel)),
        color=alt.Color(
            'variable', scale=alt.Scale(
                domain=domain,
                range=colours
            )
        ),
    ).properties(title=title)

    st.altair_chart(chart, use_container_width=True)


def bar_chart_wrapper(element, bar_data, x, y, title, domain, colours,
                      colour_var, use_container_width=True, column=None, rotation=-90):

    if column is not None:
        bar_chart = alt.Chart(bar_data, width=105).mark_bar().encode(
            x=alt.X(x, axis=alt.Axis(labelAngle=rotation)),
            y=y,
            color=alt.Color(
                colour_var, scale=alt.Scale(
                    domain=domain,
                    range=colours
                )
            ),
            column=column,
            opacity=alt.value(0.3)
        ).properties(title=title).configure_legend(orient='bottom')
    else:
        bar_chart = alt.Chart(bar_data).mark_bar().encode(
            x=alt.X(x, axis=alt.Axis(labelAngle=rotation)),
            y=y,
            color=alt.Color(
                colour_var, scale=alt.Scale(
                    domain=domain,
                    range=colours
                )
            ),
            opacity=alt.value(0.3)
        ).properties(title=title).configure_legend(orient='bottom')

    element.altair_chart(bar_chart, use_container_width=use_container_width)


def page_code():

    set_default_parameters()
    comparison_data = {}

    domain = list(st.session_state.config.simulation_presets.keys())
    colours = ['blue', 'orange', 'green', 'red', 'cyan']

    st.title("Comparison")

    st.write("Here we compare the performance of the model when simulated using the "
             "following parameter presets:")

    for preset, preset_details in st.session_state.config.simulation_presets.items():
        with st.beta_expander(preset + ": " + preset_details['preset_name']):
            st.write(preset_details['blurb'])
#########################################################################################
    st.write("The following charts show metric values averaged over the final 25 timesteps of a simulation.")

    col1, col2 = st.beta_columns([1, 1])

    col1.subheader("")
    bar_data = pd.DataFrame({
        'preset': domain,
        'terminal ROI': [
            np.mean(st.session_state.comparison_data[preset]['model_vars'].loc[-25:]['Roi'])
            for preset in domain
        ]
    })
    bar_chart_wrapper(
        col1, bar_data, x='preset', y='terminal ROI',
        title="Return on investment (ROI)",
        domain=domain, colours=colours,
        colour_var='preset',
        use_container_width=True, column=None, rotation=0
    )

    col2.subheader("")

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
    concise_load_types = ['Project', 'Slack', 'Training', 'Dept']
    bar_data['Load Type'] = [s for s in concise_load_types] * len(domain)

    bar_chart_wrapper(
        col2, bar_data, x='preset', y='Load',
        title="Workload",
        domain=concise_load_types, colours=colours,
        colour_var='Load Type',
        use_container_width=True, column=None, rotation=0
    )
#########################################################################################
    col3, col4 = st.beta_columns([1, 1])
    col3.subheader("")

    bar_data = pd.DataFrame({
        'preset': domain,
        'AverageWorkerOvr': [
            np.mean(st.session_state.comparison_data[preset]['model_vars'].loc[-25:]['AverageWorkerOvr'])
            for preset in domain
        ]
    })
    bar_chart_wrapper(
        col3, bar_data, x='preset', y='AverageWorkerOvr',
        title="Worker OVR",
        domain=domain, colours=colours,
        colour_var='preset',
        use_container_width=True, column=None, rotation=0
    )

    col4.subheader("")

    bar_data = pd.DataFrame({
        'preset': domain,
        'AverageSuccessProbability': [
            np.mean(st.session_state.comparison_data[preset]['model_vars'].loc[-25:]['AverageSuccessProbability'])
            for preset in domain
        ]
    })
    bar_chart_wrapper(
        col4, bar_data, x='preset', y='AverageSuccessProbability',
        title="Project Success Probability",
        domain=domain, colours=colours,
        colour_var='preset',
        use_container_width=True, column=None, rotation=0
    )
#########################################################################################
    st.subheader("Return on investment (ROI)")
    st.write("The following chart shows the effect of varying the skill decay on the ROI, for on the presets A-E.")

    #col5, col6 = st.beta_columns([1, 1])
    col5, = st.beta_columns([1])
    col5.subheader("")

    all_skill_decays = [0.95, 0.99, 0.995]
    all_skill_decay_data = {}

    bar_data = pd.DataFrame()
    bar_data['preset'] = [p for p in domain for s in all_skill_decays]
    bar_data['skill_decay'] = [s for s in all_skill_decays] * len(domain)

    terminal_roi_column = []
    for preset, parameters in st.session_state.config.simulation_presets.items():

        preset_e_flag = True if preset == 'E' else False
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
                load_networks=False,
                preset_e=preset_e_flag
            )
            terminal_roi_column.append(
                np.mean(all_skill_decay_data[(preset, skill_decay)]['model_vars'].loc[-25:]['Roi'])
                if all_skill_decay_data[(preset, skill_decay)]['model_vars'] is not None
                else None
            )
    bar_data['terminal ROI'] = terminal_roi_column

    bar_chart_wrapper(
        col5, bar_data, x='skill_decay:N', y='terminal ROI',
        title="",
        domain=domain, colours=colours,
        colour_var='preset',
        use_container_width=False, column='preset'
    )

    st.write("And below, we see the effect of varying the skill decay on the ROI, for on the presets A-E.")
    col6, = st.beta_columns([1])
    col6.subheader("")

    all_train_loads = [0.0, 0.1, 0.3, 2.0]
    all_train_load_data = {}

    bar_data = pd.DataFrame()
    bar_data['preset'] = [p for p in domain for s in all_train_loads]
    bar_data['train_load'] = [s if s != 2.0 else 'boost' for s in all_train_loads] * len(domain)

    terminal_roi_column = []
    for preset, parameters in st.session_state.config.simulation_presets.items():

        preset_e_flag = True if preset == 'E' else False
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
                load_networks=False,
                preset_e=preset_e_flag
            )
            terminal_roi_column.append(
                np.mean(all_train_load_data[(preset, train_load)]['model_vars'].loc[-25:]['Roi'])
                if all_train_load_data[(preset, train_load)]['model_vars'] is not None
                else None
            )
    bar_data['terminal ROI'] = terminal_roi_column

    bar_chart_wrapper(
        col6, bar_data, x='train_load:N', y='terminal ROI',
        title="",
        domain=domain, colours=colours,
        colour_var='preset',
        use_container_width=False, column='preset'
    )
#########################################################################################

    st.write("This scatter plot shows how ROI varies with worker OVR across the presets A-E.")
    chart_data = None
    for preset in st.session_state.config.simulation_presets:

        if chart_data is None:
            chart_data = (
                st.session_state.comparison_data[preset]['model_vars'][['AverageWorkerOvr', 'Roi']]
                .copy().rename(columns={'Roi': 'ROI'})
            )
            chart_data['preset'] = [preset for i in range(len(chart_data))]

        else:
            temp_data = (
                st.session_state.comparison_data[preset]['model_vars'][['AverageWorkerOvr', 'Roi']]
                .copy().rename(columns={'Roi': 'ROI'})
            )
            temp_data['preset'] = [preset for i in range(len(temp_data))]
            chart_data = chart_data.append(temp_data)

    chart = alt.Chart(chart_data).mark_circle(size=60).encode(
        x=alt.X('AverageWorkerOvr', axis=alt.Axis(title='AverageWorkerOvr'), scale=alt.Scale(domain=[30, 80])),
        y='ROI',
        color=alt.Color(
            'preset', scale=alt.Scale(
                domain=domain,
                range=colours
            )
        ),
    ).properties(title="")

    st.altair_chart(chart, use_container_width=True)
#########################################################################################

    st.subheader("Timeseries plots")
    st.write("The following timeseries plots show how the key metrics (ROI, worker OVR, team OVR) change over the "
             "course of a simulation, and compares this across the presets A-E.")
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

    time_series_plot(chart_data, domain, colours, "ROI Comparison", ylabel="ROI")

    chart_data = None
    for preset in st.session_state.config.simulation_presets:

        if chart_data is None:
            chart_data = (
                st.session_state.comparison_data[preset]['model_vars'][['time', 'AverageWorkerOvr']]
                    .copy().rename(columns={'AverageWorkerOvr': 'value'})
            )
            chart_data['variable'] = [preset for i in range(len(chart_data))]

        else:
            temp_data = (
                st.session_state.comparison_data[preset]['model_vars'][['time', 'AverageWorkerOvr']]
                    .copy().rename(columns={'AverageWorkerOvr': 'value'})
            )
            temp_data['variable'] = [preset for i in range(len(temp_data))]
            chart_data = chart_data.append(temp_data)

    time_series_plot(chart_data, domain, colours, "Worker OVR Comparison", ylabel="OVR")

    chart_data = None
    for preset in st.session_state.config.simulation_presets:

        if chart_data is None:
            chart_data = (
                st.session_state.comparison_data[preset]['model_vars'][['time', 'AverageTeamOvr']]
                .copy().rename(columns={'AverageTeamOvr': 'value'})
            )
            chart_data['variable'] = [preset for i in range(len(chart_data))]
            chart_data['value'] = moving_average(chart_data['value'], window_size=10)
        else:
            temp_data = (
                st.session_state.comparison_data[preset]['model_vars'][['time', 'AverageTeamOvr']]
                .copy().rename(columns={'AverageTeamOvr': 'value'})
            )
            temp_data['variable'] = [preset for i in range(len(temp_data))]
            temp_data['value'] = moving_average(temp_data['value'], window_size=10)
            chart_data = chart_data.append(temp_data)

    time_series_plot(chart_data, domain, colours, "Team OVR Comparison", ylabel="OVR")

