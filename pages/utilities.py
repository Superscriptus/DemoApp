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
    if 'config' not in st.session_state:
        from config import Config
        st.session_state.config = Config()

    if 'team_allocation' not in st.session_state:
        st.session_state.team_allocation = "Random"

    if 'replicate' not in st.session_state:
        st.session_state.replicate = 0

    if 'preset_active' not in st.session_state:
        st.session_state.preset_active = False

    if 'data' not in st.session_state:
        st.session_state.data = {
            'model_vars': None,
            'networks': None
        }


@st.cache()
def load_models(
        project_count, dept_workload, budget_func,
        skill_decay, train_load, rep,
        team_allocation, duration=100
):
    st.session_state.data_load_complete = False
    return_data = {}

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

    return_data['model_vars'] = unpickle(
        "data/" + sub_dir + "/%s/model_vars_rep_%d.pickle" % (optimiser_dict[team_allocation], rep)
    )
    if return_data['model_vars'] is not None:
        # We load the networks for each timestep up to 'duration' and convert them to an html string that
        # can be read by PyVis.
        return_data['networks'] = {}

        for t in range(1, duration + 1):
            #net = Network(height='400px', width='590px', bgcolor='#ffffff', font_color='white')
            net = Network(height='400px', width='85%', bgcolor='#ffffff', font_color='white')
            net.from_nx(
                nx.read_multiline_adjlist(
                    "data/" + sub_dir + "/%s/network_rep_%d_timestep_%d.adjlist"
                    % (optimiser_dict[team_allocation], rep, t)
                )
            )
            path = '/tmp'
            net.save_graph(f'{path}/pyvis_graph.html')
            html_file = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

            return_data['networks'][t - 1] = html_file.read()

        # We add ROI as this was computed and saved retrospectively (after simulations were run)
        roi = unpickle(
            "data/" + sub_dir + "/%s/roi_rep_%d.pickle" % (optimiser_dict[team_allocation], rep),
            data_type='list',
            silent=True
        )
        if roi is not None:
            return_data['model_vars']['Roi'] = moving_average(roi, window_size=10)
        else:
            return_data['model_vars']['Roi'] = np.zeros(len(st.session_state.data))

    else:
        return_data['networks'] = None

    st.session_state.data_load_complete = True

    return return_data
