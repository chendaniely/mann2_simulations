'''Run a simulation

Takes a folder as an argument.

Will create a new folder based on the config in the simulation folder.
The new folder created will be named based on the system time.

inside the timed folder will be another folder that will be a copy of
the simulation folder, augmented by some value.

This way the general folder structure will be the same during a
batch/sweep run.

'''
import argparse
import os
import glob
import datetime
import shutil
import subprocess

parser = argparse.ArgumentParser(description="Run single MANN2 simulation.")
parser.add_argument('base_sim_folder')

args = parser.parse_args()

base_sim_folder = args.base_sim_folder
base_sim_output = os.path.join('..', '..', '..', 'mann2_output')

config_file = glob.glob('{}/config*.yaml'.format(base_sim_folder))[0]
sim_script = glob.glob('{}/run_model_*.py'.format(base_sim_folder))[0]
sim_script = os.path.basename(sim_script)

now = datetime.datetime.now()
current_time = now.strftime("%Y-%m-%d_%H:%M:%S")

src = base_sim_folder
dest = os.path.join('{}'.format(base_sim_output),
                    '{}_single_{}'.format(current_time, base_sim_folder),
                    base_sim_folder)
shutil.copytree(src, dest)
os.chdir(dest)
subprocess.call(['python', sim_script])
