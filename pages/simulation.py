# TODO: - fix replicate choice so it choose from how ever many are present in the data dir
#       - refactor sidebar logic into a class
#       - refactor preset logic into a class
#       - select presets -> change sidebar widget default values
#       - change parameter values -> preset not active. Change page header.
#       - bespoke preset button with conditional formatting
#       - download main superscript repo (temporarily) and check data files size
#       - test on ipad
#       - pass variable descriptions to plot function (from config file)
#       - run new simulations (check github issues first)
#       - replace TRAIN_OFF simulation directory on github (only contains one replicate)
# Note: to change button colour and style...
# https://discuss.streamlit.io/t/how-to-change-the-backgorund-color-of-button-widget/12103/10

import streamlit as st
import altair as alt
import time
import pickle
from random import choice


def play_label(playing):
    if playing:
        return 'Stop simulation'
    else:
        return 'Play simulation'


def reload(remove_preset=False):

    if remove_preset:
        deactivate_preset()

    st.session_state.global_time = 0
    replicate = 0  # choice([i for i in range(10) if i != st.session_state.replicate])
    load_data(
        st.session_state.project_count,
        st.session_state.dept_workload,
        st.session_state.budget_func,
        st.session_state.skill_decay,
        st.session_state.train_load,
        replicate
    )


def handle_play_click():
    if st.session_state.data is not None:
        st.session_state.playing = not st.session_state.playing

    if st.session_state.global_time == 99:
        reload()


def unpickle(file_path):
    try:
        with open(file_path, 'rb') as ifile:

            df = pickle.load(ifile)
            df['time'] = df.index
            print(df.columns)

        return df

    except FileNotFoundError:
        st.error("Sorry, we do not currently have data for that parameter combination. "
                 "Please change your parameter selection. (%s)" % file_path)
        return None


def load_data(project_count, dept_workload, budget_func, skill_decay, train_load, rep):

    optimiser_dict = dict(zip(
        ['Random', 'Optimised', 'Flexible start time'],
        ['Random', 'Basin', 'Basin_w_flex']
    ))

    training_load = 0.1 if train_load == 2.0 else train_load
    training_boost = True if train_load == 2.0 else False
    training_flag = False if train_load == 0.0 else True
    sub_dir = (
            'pps_%d_sd_%.3f_dw_%.1f_tl_%.1f_tf_%d_tb_%d_bf_%d_010921_v1.1'
            % (
                project_count, skill_decay, dept_workload,
                training_load, training_flag, training_boost, budget_func
            )
    )
    #     (
    #         "pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f"
    #         % (project_count, dept_workload, budget_func, skill_decay, train_load)
    # )
    st.session_state.data = unpickle(
        "data/" + sub_dir + "/%s/model_vars_rep_%d.pickle" % (optimiser_dict[st.session_state.team_allocation], rep)
    )

    # st.session_state.worker_data = unpickle(
    #     'data/projects_per_timestep_%d/basin_w_flex/agents_vars_rep_%d.pickle' % (project_count, rep)
    # )
    # st.session_state.project_data = unpickle(
    #     'data/projects_per_timestep_%d/basin_w_flex/projects_table_rep_%d.pickle' % (project_count, rep)
    # )


class TimeSeriesPlot:

    def __init__(
            self, column_names, column_colours,
            plot_name, y_label, allow_x_axis_scrolling=False
    ):

        st.header(plot_name)

        domain_colours = dict(zip(
            column_names,
            column_colours
        ))

        column_selection = st.multiselect(
            label='Select series to plot:',
            options=list(domain_colours),
            default=list(domain_colours)
        )

        if allow_x_axis_scrolling:
            axis_scrolling = st.checkbox(
                label='Axis scrolling',
                value=True,
                key=plot_name + "_checkbox"
            )
        else:
            axis_scrolling = False

        self.domain = [s for s in column_selection]
        self.range_ = [domain_colours[d] for d in self.domain]
        self.plot_series = ['time'] + [s for s in column_selection]
        # note: updating 'selection' was messing with the contents of the slider variables
        # hence creation of a new list 'plot_series'

        _x = (
            alt.X('time', axis=alt.Axis(title='timestep'))
            if axis_scrolling else
            alt.X('time', axis=alt.Axis(title='timestep'), scale=alt.Scale(domain=[0, 100]))
        )

        chart_data = st.session_state.data.loc[
                         0:st.session_state.global_time,
                         self.plot_series
                     ].melt('time')

        chart_data['description'] = [
            st.session_state.config.simulation_variables.get(v, '(undefined)')
            for v in chart_data.variable
        ]

        base = alt.Chart(chart_data)
        points = base.mark_point(filled=True, size=40)
        line = base.mark_line()

        chart = (line + points).encode(
            x=_x,
            y=alt.Y('value', axis=alt.Axis(title=y_label)),
            color=alt.Color('variable', scale=alt.Scale(domain=self.domain, range=self.range_)),
            tooltip=['description']
        )
        self.chart = st.altair_chart(chart, use_container_width=True)

    def update(self, timestep):

        chart_data = st.session_state.data.loc[timestep:timestep, self.plot_series].melt('time')

        chart_data['description'] = [
            st.session_state.config.simulation_variables.get(v, '(undefined)')
            for v in chart_data.variable
        ]
        self.chart.add_rows(
            chart_data
        )


def deactivate_preset():
    st.session_state.preset_active = False


def preset_label(value):
    if (
            "preset" in st.session_state
            and "preset_active" in st.session_state
            and st.session_state.preset == value
            and st.session_state.preset_active
    ):
        return "!"
    else:
        return value


def create_preset_button(layout_element, value):

    with layout_element:
        st.button(
            label=preset_label(value),
            key=value,
            on_click=set_preset,
            args=value
        )


def set_preset(value):
    st.session_state.preset = value
    st.session_state.preset_active = True
    reload()


def get_preset_names(value):
    preset_dict = {
        'A': 'The Overcommitted Organization',
        'B': 'The Undercommitted Organization',
        'C': 'The Emergent Organization',
        'D': 'The Rigid Organization',
    }
    return preset_dict[value]


def set_default_parameters():

    if st.session_state.preset_active:
        preset_dict = st.session_state.config.simulation_presets[st.session_state.preset]
        st.session_state.project_count = preset_dict['project_count']
        st.session_state.budget_func = preset_dict['budget_func']

    else:
        if 'project_count' not in st.session_state:
            st.session_state.project_count = 2
        if 'budget_func' not in st.session_state:
            st.session_state.budget_func = True


def create_sidebar_controls():

    st.sidebar.subheader("Simulation parameter selection")
    speed = st.sidebar.slider(
            "Set simulation speed:",
            min_value=1,
            max_value=10,
            value=5,
            key='speed'
        )

    st.sidebar.write("Select parameter presets:")
    row_presets = st.sidebar.beta_columns([1, 1, 1, 1])
    create_preset_button(row_presets[0], "A")
    create_preset_button(row_presets[1], "B")
    create_preset_button(row_presets[2], "C")
    create_preset_button(row_presets[3], "D")

    st.sidebar.write("Set value for all parameters:")
    with st.sidebar.beta_expander("Expand for full parameter control"):

        set_default_parameters()

        row_0 = st.beta_columns([2, 1])

        with row_0[0]:
            team_allocation = st.selectbox(
                "Team allocation:",
                options=['Random', 'Optimised', 'Flexible start time'],
                key='team_allocation',
                on_change=reload,
                args=(True,),
                help="The method used for allocating a team of workers to each project.  \n"
                     "* Random: randomly assigned team.  \n"
                     "* Optimised: success probability optimised using basin-hopping algorithm.  \n"
                     "* Flexible start time: same as _Optimised_ but with flexible project start time."
            )

        with row_0[-1]:
            budget_func = st.selectbox(
                "Budget:",
                options=[True, False],
                key='budget_func',
                on_change=reload,
                args=(True,),
                format_func=lambda x: 'On' if x else 'Off',
                help="Budgetary constraint on/off."
            )

        row_1 = st.beta_columns([1, 2])

        with row_1[0]:
            project_count = st.selectbox(
                label="New projects:",
                options=[1, 2, 3, 5, 10],
                key='project_count',
                on_change=reload,
                args=(True,),
                help="Number of new projects created each time step:"
            )

        if 'dept_workload' not in st.session_state:
            st.session_state.dept_workload = 0.1

        with row_1[-1]:
            dept_workload = st.slider(
                "Departmental workload:",
                min_value=0.1,
                max_value=0.3,
                step=0.2,
                key='dept_workload',
                on_change=reload,
                args=(True,),
                help='Fraction of capacity that must be keep free to meet departmental workload.'
            )

        if 'skill_decay' not in st.session_state:
            st.session_state.skill_decay = 0.99

        skill_decay = st.radio(
            "Skill decay:",
            options=[0.950, 0.990, 0.995],
            key='skill_decay',
            on_change=reload,
            args=(True,),
            format_func=lambda x: '%.3f' % x,
            help="The multiplicative decay of worker unused hard skills.  \n"
                 "_Note: a lower value means faster decay._"
        )

        if 'train_load' not in st.session_state:
            st.session_state.train_load = 0.1

        train_load = st.selectbox(
            "Training load:",
            options=[0.0, 0.1, 0.3, 2.0],
            key='train_load',
            on_change=reload,
            args=(True,),
            format_func=lambda x: '%.1f' % x if x < 2 else 'Boost',
            help="Fraction of workforce that should be in training for any timestep.  \n"
                 "_Note: this cannot always be met if their is insufficient slack._"
        )

    if 'data' not in st.session_state:
        load_data(
            project_count=st.session_state.project_count,
            dept_workload=st.session_state.dept_workload,
            budget_func=st.session_state.budget_func,
            train_load=st.session_state.train_load,
            skill_decay=st.session_state.skill_decay,
            rep=st.session_state.replicate
        )

    if 'playing' not in st.session_state:
        st.session_state.playing = False

    if 'global_time' not in st.session_state:
        st.session_state.global_time = 0

    play = st.sidebar.button(
        play_label(st.session_state.playing),
        on_click=handle_play_click
    )


def page_code():

    if 'replicate' not in st.session_state:
        st.session_state.replicate = 0

    if 'preset_active' not in st.session_state:
        st.session_state.preset_active = False

    st.title("Simulation")

    if st.session_state.preset_active:
        st.subheader(
            "Using parameter preset %s: %s" % (
                st.session_state.preset,
                get_preset_names(st.session_state.preset)
            )
        )

    st.write("A short description of this preset and how to navigate/interpret the plots below...")

    create_sidebar_controls()

    if st.session_state.data is not None:

        active_plot = TimeSeriesPlot(
            column_names=['ActiveProjects'],
            column_colours=['blue'],
            plot_name='Active Project Count',
            y_label='number of projects'
        )

        project_plot = TimeSeriesPlot(
            column_names=['SuccessfulProjects', 'FailedProjects', 'NullProjects'],
            column_colours=['green', 'red', 'orange'],
            plot_name='Project Plot',
            y_label='number of projects'
        )

        worker_plot = TimeSeriesPlot(
            column_names=['WorkersOnProjects', 'WorkersWithoutProjects', 'WorkersOnTraining'],
            column_colours=['green', 'red', 'orange'],
            plot_name='Worker Plot',
            y_label='Number of workers'
        )

        load_plot = TimeSeriesPlot(
            column_names=['ProjectLoad', 'TrainingLoad', 'DeptLoad', 'Slack'],
            column_colours=['green', 'orange', 'red', 'blue'],
            plot_name='Load Plot',
            y_label='Fraction of capacity'
        )

        ovr_plot = TimeSeriesPlot(
            column_names=['AverageWorkerOvr', 'AverageTeamOvr'],
            column_colours=['green', 'blue'],
            plot_name='OVR Plot',
            y_label='OVR'
        )

        success_plot = TimeSeriesPlot(
            column_names=['RecentSuccessRate', 'AverageSuccessProbability'],
            column_colours=['green', 'blue'],
            plot_name='Success Plot',
            y_label='Rate / Probability'
        )

        turnover_plot = TimeSeriesPlot(
            column_names=['WorkerTurnover', 'ProjectsPerWorker', 'AverageTeamSize'],
            column_colours=['red', 'green', 'blue'],
            plot_name='Turnover Plot',
            y_label='Count'
        )

        if st.session_state.playing:
            start = st.session_state.global_time + 1

            for t in range(start, 100):

                active_plot.update(t)
                project_plot.update(t)
                worker_plot.update(t)
                ovr_plot.update(t)
                load_plot.update(t)
                success_plot.update(t)
                turnover_plot.update(t)

                time.sleep(0.2 / st.session_state.speed)
                st.session_state.global_time += 1

                if t == 99:
                    st.session_state.playing = False
                    st.experimental_rerun()
