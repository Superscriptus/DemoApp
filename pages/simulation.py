# TODO: - refactor sidebar logic into a class
#       - write script for copying data files from main SuperScript repo (folder names to include all parameter values)
#       - download main superscript repo (temporarily) and check data files size
#       - test on ipad
#       - run new simulations (check github issues first)
#       - replace TRAIN_OFF simulation directory on github (only contains one replicate)

import streamlit as st
import altair as alt
import time
import pickle
from random import choice


def play_label(playing):
    if playing:
        return 'Stop'
    else:
        return 'Play'


def reload():

    st.session_state.global_time = 0
    replicate = choice([i for i in range(10) if i != st.session_state.replicate])
    load_data(st.session_state.project_count, st.session_state.dept_workload, replicate)


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


def load_data(project_count, dept_workload, rep):

    sub_dir = "pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (project_count, dept_workload, 1, 0.99, 0.1)
    st.session_state.data = unpickle(
        "data/" + sub_dir + "/Basin_w_flex/model_vars_rep_%d.pickle" % rep
    )
    # st.session_state.worker_data = unpickle(
    #     'data/projects_per_timestep_%d/basin_w_flex/agents_vars_rep_%d.pickle' % (project_count, rep)
    # )
    # st.session_state.project_data = unpickle(
    #     'data/projects_per_timestep_%d/basin_w_flex/projects_table_rep_%d.pickle' % (project_count, rep)
    # )


class TimeSeriesPlot:

    def __init__(self, column_names, column_colours, plot_name, y_label):

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

        # Note: to change button colour and style...
        # https://discuss.streamlit.io/t/how-to-change-the-backgorund-color-of-button-widget/12103/10
        axis_scrolling = st.checkbox(
            label='Axis scrolling',
            value=True,
            key=plot_name + "_checkbox"
        )

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

        self.chart = st.altair_chart(
            alt.Chart(
                st.session_state.data.loc[
                    0:st.session_state.global_time,
                    self.plot_series
                ].melt('time')).mark_line().encode(
                x=_x,
                y=alt.Y('value', axis=alt.Axis(title=y_label)),
                color=alt.Color('variable', scale=alt.Scale(domain=self.domain, range=self.range_))
            ),
            use_container_width=True
        )

    def update(self, timestep):

        self.chart.add_rows(
            st.session_state.data.loc[timestep:timestep, self.plot_series].melt('time')
        )


def page_code():

    if 'replicate' not in st.session_state:
        st.session_state.replicate = 0

    st.title("Simulation")
    st.write("This page will show animation of a simulation (approximately like running the Mesa server).")
    st.write("Below, you can explore all the available columns in the data by selecting which ones to visualise "
             "on each plot. We can then choose which ones we want to keep in the finished product. " 
             "All of these variables are available for each of the simulations that we ran. The "
             "simulation will be selected by choosing the parameters in the sidebar (currently just number of projects,"
             " but we will add skill_decay etc).")
    st.write("You can vary the axis scrolling behaviour for each plot by toggling the 'Axis Scrolling' checkbox.")

    speed = st.sidebar.slider(
            "Set simulation speed:",
            min_value=1,
            max_value=10,
            value=5,
        )

    if 'project_count' not in st.session_state:
        st.session_state.project_count = 2

    # Note: 'key' links the widget to session state variable of same name. This is not documented behaviour?!
    project_count = st.sidebar.radio(
        "Number of new projects created each time step:",
        options=[1, 2, 3, 5, 10],
        key='project_count',
        on_change=reload
    )

    if 'dept_workload' not in st.session_state:
        st.session_state.dept_workload = 0.1

    dept_workload = st.sidebar.radio(
        "Departmental workload:",
        options=[0.1, 0.3],
        key='dept_workload',
        on_change=reload
    )

    if 'data' not in st.session_state:
        load_data(
            project_count=st.session_state.project_count,
            dept_workload=st.session_state.dept_workload,
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

                time.sleep(0.2 / speed)
                st.session_state.global_time += 1

                if t == 99:
                    st.session_state.playing = False
                    st.experimental_rerun()
