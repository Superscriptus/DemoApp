import streamlit as st
import altair as alt
import time
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import copy

from .utilities import load_models


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


def preset_e_selected():
    if "preset" in st.session_state and st.session_state.preset == "E":
        return True
    else:
        return False


def reload(remove_preset=False, rerun=True):
    """
    Note: rerun re-draws plots and widgets. Needs to run before reloading data in order to activate presets.
    """
    if remove_preset:
        deactivate_preset()

    st.session_state.global_time = 0
    st.session_state.replicate = 0  # choice([i for i in range(10) if i != st.session_state.replicate])
    if rerun:
        st.session_state.pop('simulation_data', None)
        st.experimental_rerun()
    else:
        st.session_state.simulation_data = load_models(
            project_count=st.session_state.project_count,
            dept_workload=st.session_state.dept_workload,
            budget_func=st.session_state.budget_func,
            train_load=st.session_state.train_load,
            skill_decay=st.session_state.skill_decay,
            rep=st.session_state.replicate,
            team_allocation=st.session_state.team_allocation,
            preset_e=preset_e_selected()
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

        chart_data = (
            st.session_state.simulation_data['model_vars']
              .loc[timestep:timestep, self.plot_series].melt('time')
        )

        chart_data['description'] = [
            st.session_state.config.simulation_variables.get(v, '(undefined)')
            for v in chart_data.variable
        ]
        self.chart.add_rows(
            chart_data
        )


def circle_x_y(n, grow_circle=0.2):
    theta = n * np.pi / 50
    multiplier = 1 + (np.floor(n / 100) * grow_circle)
    return multiplier * np.cos(theta), multiplier * np.sin(theta)


class NetworkPlot:

    def __init__(
            self, info,
            timestep=0, placeholder=None,
            edge_scale=20, circle_scale=0.2,
            node_scale=2
    ):

        self.turnover_count = 0

        self.edge_scale = edge_scale
        self.circle_scale = circle_scale
        self.node_scale = node_scale
        self.G = copy.deepcopy(st.session_state.simulation_data['networks'].get('init', ''))
        self.get_network_at_t(timestep)
        self.max_node_count = max(
            max(value["nodes_to_add"])
            if value["nodes_to_add"]
            else 0
            for value in st.session_state.simulation_data['networks']['diff'].values()
        )

        self.all_pos = {
            i: circle_x_y(i, self.circle_scale)
            for i in range(self.max_node_count + 1)
        }

        if st.session_state.display_net:
            st.write(info)
            self.fig = plt.figure(figsize=(10, 10))
            self.placeholder = placeholder
            self.draw_graph()

    def update_network(self, timestep):
        """
        This method assumes that g is in the correct network state for t = timestep-1
        and returns the updated state at t = timestep
        """
        # old_widths = {(e[0], e[1]): e[2]['width'] for e in g.edges(data=True)}

        diff = copy.deepcopy(st.session_state.simulation_data['networks'].get('diff', ''))
        d = diff[str(timestep + 1)]

        for n in d['nodes_to_add']:
            try:
                self.turnover_count += 1
                self.G.add_node(n)
            except:
                print("Cannot add node %d" % n)
        for n in d['nodes_to_remove']:
            try:
                self.G.remove_node(n)
            except:
                pass
                # print("Cannot remove node %d" % n)
        for e in d['edges_to_add']:
            try:
                self.G.add_edge(*e, width=1)
            except:
                print("Cannot add edge " + str(e))

        for e in d['edges_to_increment']:
            edge = e[0]
            increment = e[1]
            try:
                self.G[edge[0]][edge[1]]['width'] += increment
            except:
                self.G.add_edge(edge[0], edge[1], width=increment)

        # new_widths = {(e[0], e[1]): e[2]['width'] for e in g.edges(data=True)}
        # for w in set(list(old_widths.keys())).intersection(list(new_widths.keys())):
        #     if new_widths[w] < old_widths[w]:
        #         print("Width decrease for edge " + str(w) + " at timestep " + str(timestep))

    def get_network_at_t(self, timestep):

        if timestep == 0:
            pass
        else:
            for t in range(1, timestep + 1):
                self.update_network(t)

    def draw_graph(self):

        pos = {
            n: self.all_pos[int(n)]
            for n in self.G.nodes()
        }
        self.fig.clear()
        cc = self.G.subgraph(max(nx.connected_components(self.G), key=len))

        nx.draw_networkx(
            cc, ax=self.fig.gca(),
            pos=pos, with_labels=False,
            width=[e[2]['width'] / self.edge_scale for e in self.G.edges(data=True)],
            node_size=[10 + self.node_scale * self.G.degree[n] for n in cc.nodes()]
        )

        circle_size = 1 + self.circle_scale * (self.max_node_count / 100) + 0.1

        font = {'family': 'serif',
                'color': 'black',
                'weight': 'normal',
                'size': 13,
                }
        net_size = len(cc)
        isolates = 100 - net_size
        plt.text(
            0.62 * circle_size, .85 * circle_size,
            "Isolates: %d \nTurnover: %d\nNetwork size: %d" % (isolates, self.turnover_count, net_size),
            fontdict=font,
            bbox=dict(facecolor='blue', alpha=0.2, boxstyle='round')
        )
        plt.xlim([-circle_size, circle_size])
        plt.ylim([-circle_size, circle_size])
        plt.tight_layout()
        buf = BytesIO()
        self.fig.savefig(buf, format="png")
        self.placeholder.image(buf)

    def update(self, timestep):
        self.update_network(timestep)
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

        select_replicate()

        st.session_state.simulation_data = load_models(
            project_count=st.session_state.project_count,
            dept_workload=st.session_state.dept_workload,
            budget_func=st.session_state.budget_func,
            train_load=st.session_state.train_load,
            skill_decay=st.session_state.skill_decay,
            rep=st.session_state.replicate,
            team_allocation=st.session_state.team_allocation,
            preset_e=preset_e_selected()
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


def select_replicate(verbose=False):

    max_rep = st.session_state.config.config_params['max_replicates']
    previous_rep = st.session_state.replicate

    if st.session_state.preset_active and max_rep > 1:

        st.session_state.replicate = np.random.choice(
            [
                i for i in range(max_rep)
                if i != previous_rep
            ]
        )
    else:
        st.session_state.replicate = previous_rep

    if verbose:
        print("Selected replicate %d" % st.session_state.replicate)


def page_code():

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
        st.write("Select a parameter preset in the sidebar (A, B, C, D or E), or explore the behaviour of the "
                 "simulation by selecting your own parameter values (click 'Expand for full parameter control').  \n \n"
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

        st.subheader('Social Network')
        st.button(
            social_network_label(st.session_state.display_net),
            on_click=handle_network_click
        )
        if st.session_state.display_net:
            st.write(
                "The network of all successful collaborations between workers. Nodes represent workers and "
                "edges represent successful collaborations. The width of each edge is determined by the number of "
                "successful collaborations between that pair of workers, and the size of each node indicates the "
                "degree (i.e. number of collaborations for that worker). Workers without any successful collaborations "
                "are isolated nodes in the network and for clarity these are not depicted. When workers are replaced "
                "due to inactivity, new workers are placed to fill concentric circles of increasing radius."
            )
        placeholder = st.empty()
        net_plot = NetworkPlot(
            timestep=st.session_state.global_time,
            info="",
            placeholder=placeholder
        )

        if st.session_state.playing:
            start = st.session_state.global_time + 1

            for t in range(start, 100):

                for plot in plot_list:
                    plot.update(t)

                time.sleep(0.2 / st.session_state.speed)
                st.session_state.global_time += 1

                if st.session_state.display_net:
                    net_plot.update(t)

                if t == 99:
                    st.session_state.playing = False
                    st.experimental_rerun()
