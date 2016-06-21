import argparse
import os
import glob
import yaml
import itertools
import datetime
import shutil
import subprocess

from tqdm import tqdm

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

runs = batch_config['runs']
runs_str_fmt = 'r{{:0>{}d}}'.format(len(str(runs - 1)))

batch_sweeps = itertools.product(range(runs))

for bs in tqdm(batch_sweeps):
    run, = bs
    new_folder_name = runs_str_fmt.format(run)

    src = base_sim_folder
    dest = os.path.join('{}'.format(base_sim_output),
                        '{}_batch_{}'.format(current_time, base_sim_folder),
                        new_folder_name)
    shutil.copytree(src, dest)
    config['sim_generated_configs']['run_number'] = run
    with open(os.path.join('{}'.format(dest), config_file_basename), 'w') as f:
        f.write(yaml.dump(config, default_flow_style=False))

    print(dest)
    os.chdir(dest)
    subprocess.call(['python', sim_script_basename])
    os.chdir(HERE)
