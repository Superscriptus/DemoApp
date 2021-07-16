import streamlit as st
import numpy as np
import pandas as pd
import time


def page_code():
    st.title("Simulation")
    st.write("This tab will show animation of a simulation (approximately like running the Mesa server).")
    # st.image("images/screenshot.png")
    play = st.button('Play')

    df = pd.DataFrame(
        {
            'x': [np.sin(0)],
            'y': [np.cos(0)],
        }
    )

    chart = st.line_chart(df)

    if play:
        for t in range(1, 100):
            chart.add_rows(
                pd.DataFrame(
                    {
                        'x': [np.sin(t / 10)],
                        'y': [np.cos(t / 10)],
                    }
                )
            )
            time.sleep(0.1)
