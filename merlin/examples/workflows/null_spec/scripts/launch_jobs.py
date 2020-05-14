import argparse
import os
import shutil
import subprocess


parser = argparse.ArgumentParser(description="Launch 35 merlin workflow jobs")
parser.add_argument("run_id", type=int, help="The ID of this run")
parser.add_argument("output_path", type=str, help="the output path")
parser.add_argument("spec_path", type=str, help="path to the spec to run")
parser.add_argument("script_path", type=str, help="path to the make samples script")
args = parser.parse_args()

# launch 35 merlin workflow jobs
submit_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
concurrencies = [1, 2, 4, 8, 16, 32, 64]
nodes = [1, 1, 1, 1, 1, 1, 2]
#samples = [100000]
samples = [1, 10, 100, 1000, 10000]
output_path = os.path.join(args.output_path, f"run_{args.run_id}")
os.makedirs(output_path, exist_ok=True)
for i, concurrency in enumerate(concurrencies):
    c_name = os.path.join(output_path, f"c_{concurrency}")
    if not os.path.isdir(c_name):
        os.mkdir(c_name)
    os.chdir(c_name)
    for sample in samples:
        s_name = os.path.join(c_name, f"s_{sample}")
        if not os.path.isdir(s_name):
            os.mkdir(s_name)
        os.chdir(s_name)
        submit = f"submit_{nodes[i]}_node.sbatch"
        command = f"sbatch --jobname={run_id}{os.path.basename(args.spec_path)} {submit} {sample} {int(concurrency/nodes[i])}"
        shutil.copyfile(os.path.join(submit_path, submit), submit)
        shutil.copyfile(args.spec_path, "spec.yaml")
        os.mkdir("scripts")
        shutil.copyfile(args.script_path, os.path.join("scripts", "make_samples.py"))
        lines = subprocess.check_output(command, shell=True).decode("ascii")
        os.chdir(f"..")
    os.chdir(f"..")
