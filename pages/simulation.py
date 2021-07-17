import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time


def page_code():
    st.title("Simulation")
    st.write("This tab will show animation of a simulation (approximately like running the Mesa server).")
    st.write("(Note: Currently just showing dummy sinusoidal data.")

    speed = st.sidebar.slider(
            "Set simulation speed:",
            min_value=1,
            max_value=10,
            value=5,
        )
    play = st.sidebar.button('Play')

    domain_colours = dict(zip(
        ['successful', 'failed', 'null'],
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

    df = pd.DataFrame(
        {
            'time': 0,
            'successful': [np.sin(0)],
            'failed': [np.cos(0)],
            'null': [np.cos(0)**2],
        }
    )

    chart = st.altair_chart(
        alt.Chart(
            df[plot_series].melt('time')).mark_line().encode(
                x=alt.X('time', axis=alt.Axis(title='timestep')),
                y=alt.Y('value', axis=alt.Axis(title='number of projects')),
                color=alt.Color('variable', scale=alt.Scale(domain=domain, range=range_))
        ),
        use_container_width=True
    )

    if play:
        for t in range(1, 100):
            chart.add_rows(
                pd.DataFrame(
                    {
                        'time': t,
                        'successful': [np.sin(t / 10)],
                        'failed': [np.cos(t / 10)],
                        'null': [np.cos(t / 7)**2],
                    }
                )[plot_series].melt('time')
            )
            time.sleep(0.2 / speed)
