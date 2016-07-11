import argparse
import os
import glob
import yaml
import itertools
import datetime
from collections import OrderedDict
import shutil
from joblib import Parallel, delayed
import subprocess

import numpy as np  # used by config

from tqdm import tqdm


def set_config_value_unknown(config_dict, find_key, new_value, unknown):
    """for a given dictionary, it will recursively search for the key.
    if a key is found it will assign the new value

    if the key is not found, it will assign the key-value pair to the
    unknown key in the dictionary
    """

    def _set_config_value(config_dict, find_key, new_value):
        if find_key in config_dict:
            config_dict[find_key] = new_value
            return(config_dict)
        else:
            for stuff in config_dict:
                value = config_dict[stuff]
                if isinstance(value, dict):
                    _set_config_value(value, find_key, new_value)
                else:
                    continue
            return(None)

    def _finditem(obj, key):
        if key in obj:
            return obj[key]
        for k, v in obj.items():
            if isinstance(v, dict):
                item = _finditem(v, key)
                if item is not None:
                    return item

    does_item_exist_already = _finditem(config_dict, find_key)
    if does_item_exist_already is None:
        # if the parameter does not exist, add it to the unknown key
        config_dict[unknown][find_key] = new_value
        return(config_dict)
    else:
        # if it does exist, update the key
        new_config = _set_config_value(config_dict, find_key, new_value)
        return(new_config)


def run_simulation(simulation_path):
    os.chdir(simulation_path)
    subprocess.call(['python', sim_script_basename])
    os.chdir(HERE)


HERE = os.path.abspath(os.path.dirname(__file__))

now = datetime.datetime.now()
current_time = now.strftime("%Y-%m-%d_%H:%M:%S")

parser = argparse.ArgumentParser(description="Run single MANN2 simulation.")
parser.add_argument('base_sim_folder')

args = parser.parse_args()

base_sim_folder = args.base_sim_folder
base_sim_output = os.path.join('..', '..', '..', 'mann2_output')

config_file = glob.glob('{}/config*.yaml'.format(base_sim_folder))[0]
config_file_basename = os.path.basename(config_file)

sim_script = glob.glob('{}/run_model_*.py'.format(base_sim_folder))[0]
sim_script_basename = os.path.basename(sim_script)

with open(config_file, 'r') as config_yaml:
    config = yaml.load(config_yaml)
    batch_config = config['batch_sim']

batch_config_eval = {x: eval(batch_config[x]) for x in batch_config}
batch_config_eval = OrderedDict(batch_config_eval)

# runs_str_fmt = 'r{{:0>{}d}}'.format(len(str(runs - 1)))

batch_sweeps = (itertools.product(*batch_config_eval.values()))
batch_sweep_keys = batch_config_eval.keys()

run_counter = 0

dest_base_path = os.path.join('{}'.format(base_sim_output),
                              '{}_batch_{}'.format(current_time,
                                                   base_sim_folder))

# setup folders in output directory
for bs in tqdm(batch_sweeps):
    new_folder_name = ''
    for bs_i, bs_key in enumerate(batch_sweep_keys):
        update_value = bs[bs_i]
        update_key = bs_key[:-1]
        set_config_value_unknown(
            config, update_key, update_value, 'sim_generated_configs')
        new_folder_name = new_folder_name + \
            str(update_key[0:1]) + str(update_value) + '_'
    config['sim_generated_configs']['run_number'] = run_counter
    new_folder_name = new_folder_name[0:-1]
    src = base_sim_folder
    dest = os.path.join(dest_base_path, new_folder_name)
    shutil.copytree(src, dest)
    new_config_path = os.path.join('{}'.format(dest), config_file_basename)
    with open(new_config_path, 'w') as f:
        f.write(yaml.dump(config, default_flow_style=False))
    run_counter += 1

# find the simulation folders of interest and run the simulation
sim_folders = glob.glob('{}/*'.format(dest_base_path))

# run the simulations
# for sim in tqdm(sim_folders):
#     run_simulation(sim)

Parallel(n_jobs=-2)(delayed(run_simulation)(sim) for sim in sim_folders)
