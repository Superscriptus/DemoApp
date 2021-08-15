import streamlit as st
import altair as alt
import time
import pickle
from random import randint


def play_label(playing):
    if playing:
        return 'Stop'
    else:
        return 'Play'


def handle_play_click():
    st.session_state.playing = not st.session_state.playing

    if st.session_state.global_time == 99:
        st.session_state.global_time = 0

        replicate = randint(0, 9)
        while replicate == st.session_state.replicate:
            replicate = randint(0, 9)
            st.session_state.replicate = replicate

        st.session_state.data = load_data(replicate)


def load_data(rep=0):
    with open('data/projects_per_timestep_2/basin_w_flex/model_vars_rep_%d.pickle' % rep, 'rb') as ifile:
        df = pickle.load(ifile)
        df['time'] = df.index

    return df


def page_code():

    if 'replicate' not in st.session_state:
        st.session_state.replicate = 0

    if 'data' not in st.session_state:
        st.session_state.data = load_data(st.session_state.replicate)

    st.title("Simulation")
    st.write("This tab will show animation of a simulation (approximately like running the Mesa server).")

    speed = st.sidebar.slider(
            "Set simulation speed:",
            min_value=1,
            max_value=10,
            value=5,
        )

    if 'playing' not in st.session_state:
        st.session_state.playing = False

    if 'global_time' not in st.session_state:
        st.session_state.global_time = 0

    play = st.sidebar.button(
        play_label(st.session_state.playing),
        on_click=handle_play_click
    )

    domain_colours = dict(zip(
        ['SuccessfulProjects', 'FailedProjects', 'NullProjects'],
        ['green', 'red', 'orange']
    ))
    selection = st.multiselect(
        label='Select series to plot:',
        options=list(domain_colours),
        default=list(domain_colours)
    )

    domain = [s for s in selection]
    range_ = [domain_colours[d] for d in domain]
    plot_series = ['time'] + [s for s in selection]
    # note: updating 'selection' was messing with the contents of the slider variables
    # hence creation of a new list 'plot_series'

    chart = st.altair_chart(
        alt.Chart(
            st.session_state.data.loc[
                0:st.session_state.global_time,
                plot_series
            ].melt('time')).mark_line().encode(
                x=alt.X('time', axis=alt.Axis(title='timestep')),
                y=alt.Y('value', axis=alt.Axis(title='number of projects')),
                color=alt.Color('variable', scale=alt.Scale(domain=domain, range=range_))
        ),
        use_container_width=True
    )

    if st.session_state.playing:
        start = st.session_state.global_time + 1

        for t in range(start, 100):
            chart.add_rows(
                st.session_state.data.loc[t:t, plot_series].melt('time')
            )
            time.sleep(0.2 / speed)
            st.session_state.global_time += 1

            if t == 99:
                st.session_state.playing = False
                st.experimental_rerun()
