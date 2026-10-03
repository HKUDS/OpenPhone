import os
import shutil
import sys

folder = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("EVAL_LOG_DIR", "./logs/evaluation")
files = os.listdir(folder)

for file in files:
    if file == ".DS_Store" or file == "emulator_output.txt":
        continue
    tasks = os.listdir(os.path.join(folder, file))
    for task in tasks:
        if task == ".DS_Store":
            continue
        if not os.path.exists(os.path.join(folder, file, task, "traces/trace.jsonl")):
            print(f"Trace for task '{folder, file, task}' not found.")
            if os.path.exists(os.path.join(folder, file, task)):
                shutil.rmtree(os.path.join(folder, file, task))
