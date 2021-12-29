"""
Script to transfer data from a local copy of main SuperScript/simulation_io directory into a stripped
down version at ./data which is used to drive the Streamlit app.

usage:  python data_transfer_partial.py <path_to_simulation_io>

Note: currently only model_vars files are retained (more granular agent, project and network data are stripped out).
Note: this also limits the number of replicate simulations to 10 by default (can reduce to save space).
Note: train = 2 encodes the 'training boost' scenario
"""

import os
import sys
import shutil
import glob
import itertools


MAX_REP = 9  # Will only copy up to MAX_REP replicates

if len(sys.argv) != 2:
    raise Exception("You need to input the path to simulation_io")

sim_path = sys.argv[1]


def data_not_found(path):
    print("Could not find simulation data at: " + path)


def strip_unwanted(path, max_reps=True):

    names = ['Niter0', 'Basic']
    for name in names:
        for f in glob.glob(to_path + "/%s" % name):
            shutil.rmtree(f)

    names = ['agents', 'project', 'network_timestep']
    for name in names:
        for f in glob.glob(to_path + "/*/%s*" % name):
            os.remove(f)

    for f in glob.glob(to_path + "/*/network_rep_*_timestep_*"):
        _t = f.split('_')[4].split('.')[0]
        if _t > 1:
            os.remove(f)

    if max_reps:
        for f in glob.glob(to_path + "/*/*"):
            file_name = f.split('/')[-1]
            if 'rep' in file_name:
                rep_num = file_name.split('rep')[1].split('_')[1]
                if rep_num > MAX_REP:
                    os.remove(f)
                # if 'network' in file_name:
                #     if int(file_name.split('_')[2]) > MAX_REP:
                #         os.remove(f)
                # elif int(file_name.split('.')[0].split('rep_')[1]) > MAX_REP:
                #     os.remove(f)


def copy_data(src, dst, overwrite=False):
    if not os.path.isdir(src):
        data_not_found(src)
    else:
        if overwrite or not os.path.isdir(dst):
            shutil.copytree(src, dst)
            strip_unwanted(dst)


PPS = [1, 2, 3, 5, 10]
SD = [0.95, 0.99, 0.995]
DW = [0.1, 0.3]
TL = [0.1, 0.3, 0.0, 2.0]
BF = [0, 1]

combinations = list(itertools.product(PPS, SD, DW, TL, BF))

for parameters in combinations:

    new_projects = parameters[0]
    skill_decay = parameters[1]
    departmental_workload = parameters[2]
    training_load = 0.1 if parameters[3] == 2.0 else parameters[3]
    training_boost = True if parameters[3] == 2.0 else False
    training_flag = False if training_load == 0.0 else True
    budget_functionality = parameters[4]

    batch_name = (
            'pps_%d_sd_%.3f_dw_%.1f_tl_%.1f_tf_%d_tb_%d_bf_%d_010921_v1.1'
            % (
                new_projects, skill_decay, departmental_workload,
                training_load, training_flag, training_boost, budget_functionality
            )
    )

    from_path = sim_path + batch_name
    to_path = 'data/' + batch_name
    copy_data(from_path, to_path, overwrite=True)

## Now run Preset E transfer:
combinations = [
        [3, 0.95, 0.1, 0.1, 1],
        [3, 0.99, 0.1, 0.1, 1],
        [3, 0.995, 0.1, 0.1, 1],
        [3, 0.995, 0.1, 0.0, 1],
        [3, 0.995, 0.1, 0.3, 1],
        [3, 0.995, 0.1, 2.0, 1]
    ]

for parameters in combinations:

    new_projects = parameters[0]
    skill_decay = parameters[1]
    departmental_workload = parameters[2]
    training_load = 0.1 if parameters[3] == 2.0 else parameters[3]
    training_boost = True if parameters[3] == 2.0 else False
    training_flag = False if training_load == 0.0 else True
    budget_functionality = parameters[4]

    batch_name = (
            'preset_E_sd_%.3f_tl_%.1f_tf_%d_tb_%d_251021_v1.1'
            % (skill_decay, training_load, training_flag, training_boost)
    )

    from_path = sim_path + batch_name
    to_path = 'data/' + batch_name
    copy_data(from_path, to_path, overwrite=True)

