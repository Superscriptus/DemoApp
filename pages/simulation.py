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
    st.session_state.data = load_data(st.session_state.project_count, replicate)


def handle_play_click():
    if st.session_state.data is not None:
        st.session_state.playing = not st.session_state.playing

    if st.session_state.global_time == 99:
        reload()


def load_data(project_count, rep):

    try:
        with open(
                'data/projects_per_timestep_%d/basin_w_flex/model_vars_rep_%d.pickle' % (project_count, rep), 'rb'
        ) as ifile:

            df = pickle.load(ifile)
            df['time'] = df.index
            print(df.columns)

        return df

    except FileNotFoundError:
        st.error("Sorry, we do not currently have data for that parameter combination. "
                 "Please change your parameter selection."
                 'data/projects_per_timestep_%d/basin_w_flex/model_vars_rep_%d.pickle' % (project_count, rep))
        return None


class TimeSeriesPlot:

    def __init__(self, column_names, column_colours, plot_name=None):

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
            value=True
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
                y=alt.Y('value', axis=alt.Axis(title='number of projects')),
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

    if 'data' not in st.session_state:
        st.session_state.data = load_data(
            project_count=st.session_state.project_count,
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

        project_plot = TimeSeriesPlot(
            column_names=['SuccessfulProjects', 'FailedProjects', 'NullProjects'],
            column_colours=['green', 'red', 'orange']
        )

        if st.session_state.playing:
            start = st.session_state.global_time + 1

            for t in range(start, 100):

                project_plot.update(t)
                time.sleep(0.2 / speed)
                st.session_state.global_time += 1

                if t == 99:
                    st.session_state.playing = False
                    st.experimental_rerun()
