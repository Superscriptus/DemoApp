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
#       - change font size (for infoboxes) if desired: https://discuss.streamlit.io/t/change-font-size-and-font-color/12377/3
#       - could refactor Network and Timeseries plot to inherit shared logic from a base class
# Note: to change button colour and style...
# https://discuss.streamlit.io/t/how-to-change-the-backgorund-color-of-button-widget/12103/10
# Note: to change pyplot width, convert to image:
#  https://discuss.streamlit.io/t/cannot-change-matplotlib-figure-size/10295/8

import streamlit as st
import streamlit.components.v1 as components
import altair as alt
import time
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt

from .utilities import load_models, create_session_state_variables


@st.cache()
def play_label(playing):
    if playing:
        return 'Stop simulation'
    else:
        return 'Play simulation'


@st.cache()
def social_network_label(display_net):
    if display_net:
        return 'Turn off social network'
    else:
        return 'Turn on social network'


def reload(remove_preset=False, rerun=True):
    """
    Note: rerun re-draws plots and widgets. Needs to run before reloading data in order to activate presets.
    """
    if remove_preset:
        deactivate_preset()

    st.session_state.global_time = 0
    st.session_state.replicate = 0  # choice([i for i in range(10) if i != st.session_state.replicate])
    if rerun:
        del st.session_state['simulation_data']
        st.experimental_rerun()
    else:
        st.session_state.simulation_data = load_models(
            project_count=st.session_state.project_count,
            dept_workload=st.session_state.dept_workload,
            budget_func=st.session_state.budget_func,
            train_load=st.session_state.train_load,
            skill_decay=st.session_state.skill_decay,
            rep=st.session_state.replicate,
            team_allocation=st.session_state.team_allocation
        )


def handle_play_click():

    if st.session_state.data_load_complete:

        if st.session_state.simulation_data['model_vars'] is not None:
            st.session_state.playing = not st.session_state.playing

        if st.session_state.global_time == 99:
            reload()

    else:
        st.error("Attempted to play simulation while model still loading! "
                 "Please select another parameter combination and wait for model loading to complete.")


def handle_speed_slider():

    if not st.session_state.data_load_complete:
        st.error("Attempted to change simulation speed while model still loading! "
                 "Please select another Preset and wait for data load to complete.")


def handle_network_click():
    st.session_state.display_net = ~st.session_state.display_net


class TimeSeriesPlot:

    def __init__(
            self, column_names, column_colours,
            plot_name, y_label, info,
            allow_x_axis_scrolling=False,
            use_moving_average=False
    ):

        st.subheader(plot_name)
        st.write(info)

        domain_colours = dict(zip(
            column_names,
            column_colours
        ))

        column_selection = list(domain_colours)

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

        chart_data = st.session_state.simulation_data['model_vars'].loc[
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

        chart_data = st.session_state.simulation_data['model_vars'].loc[timestep:timestep, self.plot_series].melt('time')

        chart_data['description'] = [
            st.session_state.config.simulation_variables.get(v, '(undefined)')
            for v in chart_data.variable
        ]
        self.chart.add_rows(
            chart_data
        )


class NetworkPlot:

    def __init__(self, plot_name, info, timestep=0):
        st.subheader(plot_name)

        # self.G = nx.karate_club_graph()
        self.G = st.session_state.simulation_data['networks'].get(timestep, '')
        # self.g4 = Network(height='400px', width='85%', bgcolor='#ffffff', font_color='white')

        # st.button(
        #     social_network_label(st.session_state.display_net),
        #     on_click=handle_network_click
        # )

        # if st.session_state.display_net:
        st.write(info)
        self.fig = plt.figure(figsize=(20, 15))
        self.placeholder = st.empty()
        self.placeholder.pyplot(self.fig)
        self.draw_graph()
            # path = '/tmp'
            # self.g4.save_graph(f'{path}/pyvis_graph.html')
            # html_file = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')
            #
            # self.chart = components.html(
            #     #st.session_state.simulation_data['networks'].get(timestep, ''),
            #     html_file.read(),
            #     height=435
            # )

    def draw_graph(self):
        self.fig.clear()
        nx.draw_networkx(self.G, ax=self.fig.gca(), pos=nx.circular_layout(self.G))
        self.placeholder.pyplot(self.fig)
        # self.g4.from_nx(self.G)
        # path = '/tmp'
        # self.g4.save_graph(f'{path}/pyvis_graph.html')
        # html_file = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

        # with st.empty():

            # self.chart = components.html(
            #     # st.session_state.simulation_data['networks'].get(timestep, ''),
            #     html_file.read(),
            #     height=435
            # )

    def update(self, timestep):
        self.G = st.session_state.simulation_data['networks'].get(timestep, '')
        # self.G.add_node(timestep*100)
        # self.G.add_edge(0, timestep*100)
        self.draw_graph()
        pass


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
            args=value,
            help=st.session_state.config.simulation_presets[value]['preset_name']
        )


def set_preset(value):
    st.session_state.preset = value
    st.session_state.preset_active = True
    reload(remove_preset=False, rerun=True)


@st.cache()
def get_preset_details(value, detail='preset_name'):
    preset_dict = st.session_state.config.simulation_presets[value]
    return preset_dict[detail]


def set_default_parameters():
    if st.session_state.preset_active:
        parameter_dict = st.session_state.config.simulation_presets[st.session_state.preset]
        for key, value in parameter_dict.items():
            st.session_state[key] = value

    else:
        parameter_dict = st.session_state.config.default_simulation_parameters
        for key, value in parameter_dict.items():
            if key not in st.session_state:
                st.session_state[key] = value


def create_sidebar_controls():

    st.sidebar.write("Select parameter presets:")
    row_presets = st.sidebar.beta_columns([1, 1, 1, 1, 1])
    create_preset_button(row_presets[0], "A")
    create_preset_button(row_presets[1], "B")
    create_preset_button(row_presets[2], "C")
    create_preset_button(row_presets[3], "D")
    create_preset_button(row_presets[4], "E")

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
                args=(True, False),
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
                args=(True, False),
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
                args=(True, False),
                help="Number of new projects created each time step."
            )

        with row_1[-1]:
            dept_workload = st.slider(
                "Departmental workload:",
                min_value=0.1,
                max_value=0.3,
                step=0.2,
                key='dept_workload',
                on_change=reload,
                args=(True, False),
                help='Fraction of capacity that must be keep free to meet departmental workload.'
            )

        skill_decay = st.radio(
            "Skill decay:",
            options=[0.950, 0.990, 0.995],
            key='skill_decay',
            on_change=reload,
            args=(True, False),
            format_func=lambda x: '%.3f' % x,
            help="The multiplicative decay of worker unused hard skills.  \n"
                 "_Note: a lower value means faster decay._"
        )

        train_load = st.selectbox(
            "Training load:",
            options=[0.0, 0.1, 0.3, 2.0],
            key='train_load',
            on_change=reload,
            args=(True, False),
            format_func=lambda x: '%.1f' % x if x < 2 else 'Boost',
            help="Fraction of workforce that should be in training for any timestep.  \n"
                 "_Note: this cannot always be met if their is insufficient slack._"
        )

    if 'simulation_data' not in st.session_state or st.session_state.simulation_data['model_vars'] is None:
        st.session_state.simulation_data = load_models(
            project_count=st.session_state.project_count,
            dept_workload=st.session_state.dept_workload,
            budget_func=st.session_state.budget_func,
            train_load=st.session_state.train_load,
            skill_decay=st.session_state.skill_decay,
            rep=st.session_state.replicate,
            team_allocation=st.session_state.team_allocation
        )

    if 'playing' not in st.session_state:
        st.session_state.playing = False

    if 'global_time' not in st.session_state:
        st.session_state.global_time = 0

    if st.session_state.data_load_complete:

        st.sidebar.subheader("Simulation parameter selection")
        speed = st.sidebar.slider(
            "Set simulation speed:",
            min_value=1,
            max_value=10,
            value=5,
            key='speed',
            on_change=handle_speed_slider
        )

        play = st.sidebar.button(
            play_label(st.session_state.playing),
            on_click=handle_play_click
        )


def page_code():

    # if 'replicate' not in st.session_state:
    #     st.session_state.replicate = 0
    #
    # if 'preset_active' not in st.session_state:
    #     st.session_state.preset_active = False
    #
    # if 'display_net' not in st.session_state:
    #     st.session_state.display_net = False
    #
    # if 'data_load_complete' not in st.session_state:
    #     st.session_state.data_load_complete = False

    st.title("Simulation")

    if st.session_state.preset_active:
        st.subheader(
            "Using parameter preset %s: %s" % (
                st.session_state.preset,
                get_preset_details(st.session_state.preset, detail='preset_name')
            )
        )
        st.write(get_preset_details(st.session_state.preset, detail='blurb'))

    else:
        st.write("Select a parameter preset in the sidebar (A, B, C or D), or explore the behaviour of the simulation "
                 "by selecting your own parameter values (click 'Expand for full parameter control').  \n  \n"
                 "Click 'Play simulation' to run the agent-based model for your chosen parameter values.")

    create_sidebar_controls()

    if st.session_state.simulation_data['model_vars'] is not None:

        plot_list = []
        for plot, details in st.session_state.config.simulation_plots.items():
            plot_list.append(
                TimeSeriesPlot(
                    column_names=details['column_names'],
                    column_colours=details['column_colours'],
                    plot_name=plot,
                    y_label=details['y_label'],
                    info=details['info']
                )
            )

        net_plot = NetworkPlot(
            plot_name='Social Network',
            timestep=st.session_state.global_time,
            info="The network of all successful collaborations between workers."
        )

        if st.session_state.playing:
            start = st.session_state.global_time + 1

            for t in range(start, 100):

                net_plot.update(t)
                for plot in plot_list:
                    plot.update(t)

                time.sleep(0.2 / st.session_state.speed)
                st.session_state.global_time += 1

                # if st.session_state.display_net and t % 10 == 0:
                #     st.experimental_rerun()

                if t == 99:
                    st.session_state.playing = False
                    # reload(rerun=False)
                    st.experimental_rerun()
