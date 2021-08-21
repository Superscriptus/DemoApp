"""
Script to transfer data from a local copy of main SuperScript/simulation_io directory into a stripped
down version at ./data which is used to drive the Streamlit app.

usage:  python data_transfer.py <path_to_simulation_io>

Note: currently only model_vars files are retained (more granular agent, project and network data are stripped out).
"""

import os
import sys
import shutil
import glob

if len(sys.argv) != 2:
    raise Exception("You need to input the path to simulation_io")

sim_path = sys.argv[1]


def data_not_found(path):
    print("Could not find simulation data at: " + path)


def strip_unwanted(path):

    names = ['agents', 'project', 'network']
    for name in names:
        for f in glob.glob(to_path + "/*/%s*" % name):
            os.remove(f)


# First we copy the standard parameters simulations for all numbers of project_per_timstep
PPS = [1, 2, 3, 5, 10]

for pps in PPS:
    from_path = sim_path + "/project_per_step_%d_230521_v1.0" % pps
    to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, 0.1, 1, 0.99, 0.1)

    if not os.path.isdir(from_path):
        data_not_found(from_path)
    if not os.path.isdir(to_path):
        shutil.copytree(from_path, to_path)
        strip_unwanted(to_path)
