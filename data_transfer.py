"""
Script to transfer data from a local copy of main SuperScript/simulation_io directory into a stripped
down version at ./data which is used to drive the Streamlit app.

usage:  python data_transfer.py <path_to_simulation_io>

Note: currently only model_vars files are retained (more granular agent, project and network data are stripped out).
Note: this also limits the number of replicate simulations to 10 by default (can reduce to save space).
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


def strip_unwanted(path, max_ten_reps=True):

    names = ['agents', 'project', 'network']
    for name in names:
        for f in glob.glob(to_path + "/*/%s*" % name):
            os.remove(f)

    if max_ten_reps:
        for f in glob.glob(to_path + "/*/*"):
            file_name = f.split('/')[-1]
            if 'rep' in file_name and int(file_name.split('.')[0].split('rep_')[1]) > 9:
                os.remove(f)


def copy_data(src, dst):
    if not os.path.isdir(src):
        data_not_found(src)
    if not os.path.isdir(dst):
        shutil.copytree(src, dst)
        strip_unwanted(dst)


# First we copy the standard parameters simulations for all numbers of project_per_timestep
PPS = [1, 2, 3, 5, 10]

for pps in PPS:
    from_path = sim_path + "/project_per_step_%d_230521_v1.0" % pps
    to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, 0.1, 1, 0.99, 0.1)
    copy_data(from_path, to_path)

# Now we copy the extra skill decay files:
dwl = 0.1
sd = 0.95
for pps in PPS:
    from_path = sim_path + "/new_skill_decay_project_per_step_%d_110621_v1.0" % pps
    to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, dwl, 1, sd, 0.1)
    copy_data(from_path, to_path)

dwl = 0.1
sd = 0.995
for pps in PPS:
    from_path = sim_path + "/skill_decay_0995_project_per_step_%d_240621_v1.0" % pps
    to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, dwl, 1, sd, 0.1)
    copy_data(from_path, to_path)

dwl = 0.3
pps = 2
sd = 0.95
from_path = sim_path + "/new_skill_decay_project_per_step_%d_dep_wl_03_110621_v1.0" % pps
to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, dwl, 1, sd, 0.1)
copy_data(from_path, to_path)

sd = 0.995
from_path = sim_path + "/skill_decay_0995_project_per_step_%d_dep_wl_03_240621_v1.0" % pps
to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, dwl, 1, sd, 0.1)
copy_data(from_path, to_path)


# Now we copy one-off extra files:
pps = 2
dwl = 0.3
from_path = sim_path + "/deptwl_%.1f_r10_010421_v0.1" % dwl
to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, dwl, 1, 0.99, 0.1)
copy_data(from_path, to_path)

dwl = 0.6
from_path = sim_path + "/deptwl_%.1f_r5_050421_v0.1" % dwl
to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, dwl, 1, 0.99, 0.1)
copy_data(from_path, to_path)

pps = 2
dwl = 0.1
budget = 0
from_path = sim_path + "/budget_noflex_r20_030421_v0.1"
to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, dwl, budget, 0.99, 0.1)
copy_data(from_path, to_path)

# Finally, we copy the files with different training parameters:
pps = 2
dwl = 0.1
budget = 1
train = 0
from_path = sim_path + "/train_off_r1_050421_v0.1"
to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, dwl, budget, 0.99, train)
copy_data(from_path, to_path)

train = 0.3
from_path = sim_path + "/trainload_0.3_r10_030421_v0.1"
to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, dwl, budget, 0.99, train)
copy_data(from_path, to_path)

train = 2
from_path = sim_path + "/trainboost_r10_010421_v0.1"
to_path = "data/pps_%d_dwl_%.1f_budget_%d_sd_%.3f_train_%.1f" % (pps, dwl, budget, 0.99, train)
copy_data(from_path, to_path)
