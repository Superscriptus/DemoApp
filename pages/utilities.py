import pickle
import numpy as np
import streamlit as st
import networkx as nx
from pyvis.network import Network


def unpickle(file_path, data_type='df', silent=False):
    try:
        with open(file_path, 'rb') as ifile:

            if data_type == 'df':
                data = pickle.load(ifile)
                data['time'] = data.index

            elif data_type == 'list':
                data = np.asarray(pickle.load(ifile))

        return data

    except FileNotFoundError:
        if not silent:
            st.error("Sorry, we do not currently have data for that parameter combination. "
                     "Please change your parameter selection. (%s)" % file_path)
        return None


@st.cache()
def moving_average(interval, window_size, append_to_len=True, look_back=2):
    window = np.ones(int(window_size)) / float(window_size)

    filtered = np.convolve(interval, window, 'valid')

    if append_to_len:
        filtered = list(filtered)
        for i in range(len(filtered), len(interval)):
            filtered.append(np.mean(interval[i - look_back:]))

    return filtered


def create_session_state_variables():

    if 'team_allocation' not in st.session_state:
        st.session_state.team_allocation = "Random"

    if 'replicate' not in st.session_state:
        st.session_state.replicate = 0

    if 'preset_active' not in st.session_state:
        st.session_state.preset_active = False


def load_data(
        project_count, dept_workload, budget_func,
        skill_decay, train_load, rep, duration=100
):
    st.session_state.data_load_complete = False

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

    st.session_state.data = unpickle(
        "data/" + sub_dir + "/%s/model_vars_rep_%d.pickle" % (optimiser_dict[st.session_state.team_allocation], rep)
    )
    if st.session_state.data is not None:
        # We load the networks for each timestep up to 'duration' and convert them to an html string that
        # can be read by PyVis.
        st.session_state.networks = {}

        for t in range(1, duration + 1):
            #net = Network(height='400px', width='590px', bgcolor='#ffffff', font_color='white')
            net = Network(height='400px', width='85%', bgcolor='#ffffff', font_color='white')
            net.from_nx(
                nx.read_multiline_adjlist(
                    "data/" + sub_dir + "/%s/network_rep_%d_timestep_%d.adjlist"
                    % (optimiser_dict[st.session_state.team_allocation], rep, t)
                )
            )
            path = '/tmp'
            net.save_graph(f'{path}/pyvis_graph.html')
            html_file = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

            st.session_state.networks[t - 1] = html_file.read()

        # We add ROI as this was computed and saved retrospectively (after simulations were run)
        roi = unpickle(
            "data/" + sub_dir + "/%s/roi_rep_%d.pickle" % (optimiser_dict[st.session_state.team_allocation], rep),
            data_type='list',
            silent=True
        )
        if roi is not None:
            st.session_state.data['Roi'] = moving_average(roi, window_size=10)
        else:
            st.session_state.data['Roi'] = np.zeros(len(st.session_state.data))

    else:
        st.session_state.networks = None

    st.session_state.data_load_complete = True
