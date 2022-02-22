import pandas as pd
import streamlit as st
import numpy as np
import altair as alt

from .utilities import load_models, moving_average
from .simulation import set_default_parameters


def time_series_plot(chart_data, domain, colours, title, ylabel, element=None):

    _x = alt.X('time', axis=alt.Axis(title='timestep'))

    if title == "Team OVR Comparison":
        dash_condition = alt.condition(
            alt.datum.variable == 'E',
            alt.value([5, 5]),
            alt.value([0])
        )
    else:
        dash_condition = alt.condition(
            alt.datum.variable == 'E',
            alt.value([0]),
            alt.value([0])
        )

    chart = alt.Chart(chart_data).mark_line().encode(
        x=_x,
        y=alt.Y('value', axis=alt.Axis(title=ylabel)),
        color=alt.Color(
            'variable', scale=alt.Scale(
                domain=domain,
                range=colours
            )
        ),
        strokeDash=dash_condition,
        tooltip=[alt.Tooltip('value', format='.2f', title=ylabel)]
    ).properties(title=title)

    if element is None:
        st.altair_chart(chart, use_container_width=True)
    else:
        element.altair_chart(chart, use_container_width=True)


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
            opacity=alt.value(0.3),
            tooltip=[alt.Tooltip(y, format='.2f')]
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
            opacity=alt.value(0.3),
            tooltip=[alt.Tooltip(y, format='.2f')]
        ).properties(title=title).configure_legend(orient='bottom')

    element.altair_chart(bar_chart, use_container_width=use_container_width)


def load_method_comparison_data(max_rep):
    """Loads data for the comparison of team allocation methods that are not loaded as presets
    into the comparison data on application launch.

    Note: May want to move this loading to application launch also
    """

    allocation_methods = {
        'Random': {
            'method': 'Random',
            'budget_flag': True
        },
        'Optimised': {
            'method': 'Optimised',
            'budget_flag': True
        },
        'Flexible start': {
            'method': 'Flexible start time',
            'budget_flag': True
        },
        'Flexible w/o budget': {
            'method': 'Flexible start time',
            'budget_flag': False
        }
    }
    parameter_dict = st.session_state.config.allocation_comparison_parameters

    method_comparison_data = {
        allocator: {
            rep: {}
            for rep in range(max_rep)
        }
        for allocator in allocation_methods.keys()
    }

    for allocator, method_dict in allocation_methods.items():
        for rep in range(max_rep):

            method_comparison_data[allocator][rep] = load_models(
                project_count=parameter_dict['project_count'],
                dept_workload=parameter_dict['dept_workload'],
                budget_func=method_dict['budget_flag'],
                train_load=parameter_dict['train_load'],
                skill_decay=parameter_dict['skill_decay'],
                rep=rep,
                team_allocation=method_dict['method'],
                preset_e=parameter_dict['preset_e_flag'],
                use_preloaded_data=False
            )

    return allocation_methods, method_comparison_data


def page_code():

    set_default_parameters()

    domain = list(st.session_state.config.simulation_presets.keys())
    colours = ['blue', 'orange', 'green', 'red', 'cyan']

    st.title("Comparison")

#########################################################################################
    # First we compute the source data for the charts by averaging over the replicate simulations:
    # (Note: could add switch to allow visualistion of individual simulation runs?)
    max_rep = st.session_state.config.config_params['max_replicates']
    max_rep_method_comparison = st.session_state.config.allocation_comparison_parameters['replicate_count']

    allocation_methods, method_comparison_data = load_method_comparison_data(max_rep_method_comparison)

    if max_rep == 1:
        source_data = {
            preset: st.session_state.comparison_data[preset][st.session_state.replicate]['model_vars']
            for preset in st.session_state.config.simulation_presets.keys()
        }

    else:
        source_data = {}
        for preset in st.session_state.config.simulation_presets.keys():
            df_list = [
                st.session_state.comparison_data[preset][rep]['model_vars']
                for rep in range(max_rep)
            ]
            df_concat = pd.concat(df_list)
            source_data[preset] = df_concat.groupby(df_concat.index).mean()

    if max_rep_method_comparison == 1:
        aggregated_pure_comparison_data = {
            allocator: method_comparison_data[allocator][st.session_state.replicate]['model_vars']
            for allocator in allocation_methods.keys()
        }
    else:
        aggregated_pure_comparison_data = {}
        for allocator in allocation_methods.keys():
            df_list_pure = [
                method_comparison_data[allocator][rep]['model_vars']
                for rep in range(max_rep_method_comparison)
            ]
            df_concat_pure = pd.concat(df_list_pure)
            aggregated_pure_comparison_data[allocator] = df_concat_pure.groupby(df_concat_pure.index).mean()


#########################################################################################
    st.subheader("Comparison between team allocation methods.")
    st.write("First we make a direct comparison between four different team allocation methods: ")
    st.write(
        """
        1. Random team allocation.
        2. Optimized team allocation (using our numerical optimization to maximise project success probability).
        3. Optimized team allocation, with flexible project start time.
        4. Optimized team allocation, flexible start time and no budget constraint on teams.
        
        Note: These plots show simulation results for 5 projects per timestep. Other parameter values are equal to 
        those of preset C (defined below).
        """
    )
    method_colours = ['red', 'orange', 'blue',  'green']
    col0a, col0b = st.beta_columns([2, 1])

    col0a.subheader("")
    bar_data = pd.DataFrame({
        'team allocator': allocation_methods.keys(),
        'terminal ROI': [
            np.mean(aggregated_pure_comparison_data[allocator].loc[-25:]['Roi'])
            for allocator in allocation_methods.keys()
        ]
    })
    bar_chart = alt.Chart(bar_data).mark_bar().encode(
        x=alt.X('team allocator', axis=alt.Axis(labelAngle=90), sort=list(allocation_methods.keys())),
        y='terminal ROI',
        color=alt.Color(
            'team allocator', scale=alt.Scale(
                domain=list(allocation_methods.keys()),
                range=method_colours
            ),
            legend=None
        ),
        opacity=alt.value(0.3),
        tooltip=[alt.Tooltip('terminal ROI', format='.2f')]
    ).properties(padding={"left": 5, "top": 30, "right": 5, "bottom": 5})
    col0b.altair_chart(bar_chart, use_container_width=True)

    chart_data = None
    for allocator in allocation_methods.keys():

        if chart_data is None:
            chart_data = (
                aggregated_pure_comparison_data[allocator][['time', 'Roi']]
                .copy().rename(columns={'Roi': 'value'})
            )
            chart_data['variable'] = [allocator for i in range(len(chart_data))]

        else:
            temp_data = (
                aggregated_pure_comparison_data[allocator][['time', 'Roi']]
                .copy().rename(columns={'Roi': 'value'})
            )
            temp_data['variable'] = [allocator for i in range(len(temp_data))]
            chart_data = chart_data.append(temp_data)

    time_series_plot(
        chart_data, list(allocation_methods.keys()),
        method_colours, "",
        ylabel="ROI", element=col0a
    )

#########################################################################################

    st.subheader("Comparison between simulation presets [A-E].")
    st.write("Now we compare the performance of the model when simulated using the "
             "following parameter presets:")

    for preset, preset_details in st.session_state.config.simulation_presets.items():
        with st.beta_expander(preset + ": " + preset_details['preset_name']):
            st.write(preset_details['blurb'])

    st.write("The following charts show metric values averaged over the final 25 timesteps of a simulation.")

    col1, col2 = st.beta_columns([1, 1])

    col1.subheader("")
    bar_data = pd.DataFrame({
        'preset': domain,
        'terminal ROI': [
            np.mean(source_data[preset].loc[-25:]['Roi'])
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
                np.mean(source_data[preset].loc[-25:][lt])
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
            np.mean(source_data[preset].loc[-25:]['AverageWorkerOvr'])
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
            np.mean(source_data[preset].loc[-25:]['AverageSuccessProbability'])
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

            df_list = []
            for rep in range(st.session_state.config.config_params['max_replicates']):

                df_list.append(
                    load_models(
                        project_count=parameter_dict['project_count'],
                        dept_workload=parameter_dict['dept_workload'],
                        budget_func=parameter_dict['budget_func'],
                        train_load=parameter_dict['train_load'],
                        skill_decay=skill_decay,
                        rep=rep,
                        team_allocation=parameter_dict['team_allocation'],
                        load_networks=False,
                        preset_e=preset_e_flag,
                        use_preloaded_data=False
                    )['model_vars']
                )

            df_concat = pd.concat(df_list)
            all_skill_decay_data[(preset, skill_decay)] = df_concat.groupby(df_concat.index).mean()

            terminal_roi_column.append(
                np.mean(all_skill_decay_data[(preset, skill_decay)].loc[-25:]['Roi'])
                if all_skill_decay_data[(preset, skill_decay)] is not None
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

    st.write("And below, we see the effect of varying the training load on the ROI, for on the presets A-E.")
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

            df_list = []
            for rep in range(st.session_state.config.config_params['max_replicates']):
                df_list.append(
                    load_models(
                        project_count=parameter_dict['project_count'],
                        dept_workload=parameter_dict['dept_workload'],
                        budget_func=parameter_dict['budget_func'],
                        train_load=train_load,
                        skill_decay=parameter_dict['skill_decay'],
                        rep=rep,
                        team_allocation=parameter_dict['team_allocation'],
                        load_networks=False,
                        preset_e=preset_e_flag,
                        use_preloaded_data=False
                    )['model_vars']
                )

            df_concat = pd.concat(df_list)
            all_train_load_data[(preset, train_load)] = df_concat.groupby(df_concat.index).mean()

            terminal_roi_column.append(
                np.mean(all_train_load_data[(preset, train_load)].loc[-25:]['Roi'])
                if all_train_load_data[(preset, train_load)] is not None
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
                source_data[preset][['AverageWorkerOvr', 'Roi']]
                .copy().rename(columns={'Roi': 'ROI'})
            )
            chart_data['preset'] = [preset for i in range(len(chart_data))]

        else:
            temp_data = (
                source_data[preset][['AverageWorkerOvr', 'Roi']]
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
        tooltip=[
            alt.Tooltip('AverageWorkerOvr', format='.2f'),
            alt.Tooltip('ROI', format='.2f')
        ]
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
                source_data[preset][['time', 'Roi']]
                .copy().rename(columns={'Roi': 'value'})
            )
            chart_data['variable'] = [preset for i in range(len(chart_data))]

        else:
            temp_data = (
                source_data[preset][['time', 'Roi']]
                .copy().rename(columns={'Roi': 'value'})
            )
            temp_data['variable'] = [preset for i in range(len(temp_data))]
            chart_data = chart_data.append(temp_data)

    time_series_plot(chart_data, domain, colours, "ROI Comparison", ylabel="ROI")

    chart_data = None
    for preset in st.session_state.config.simulation_presets:

        if chart_data is None:
            chart_data = (
                source_data[preset][['time', 'AverageWorkerOvr']]
                .copy().rename(columns={'AverageWorkerOvr': 'value'})
            )
            chart_data['variable'] = [preset for i in range(len(chart_data))]

        else:
            temp_data = (
                source_data[preset][['time', 'AverageWorkerOvr']]
                .copy().rename(columns={'AverageWorkerOvr': 'value'})
            )
            temp_data['variable'] = [preset for i in range(len(temp_data))]
            chart_data = chart_data.append(temp_data)

    time_series_plot(chart_data, domain, colours, "Worker OVR Comparison", ylabel="OVR")

    chart_data = None
    for preset in st.session_state.config.simulation_presets:

        temp_data = (
            source_data[preset][['time', 'AverageTeamOvr']]
            .copy().rename(columns={'AverageTeamOvr': 'value'})
        )
        temp_data['variable'] = [preset for i in range(len(temp_data))]
        temp_data['value'] = moving_average(temp_data['value'], window_size=10)

        if chart_data is None:
            chart_data = temp_data
        else:
            chart_data = chart_data.append(temp_data)

    time_series_plot(chart_data, domain, colours, "Team OVR Comparison", ylabel="OVR")

