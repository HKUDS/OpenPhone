import os
import argparse

from agent import get_agent
from config_env import load_config
from evaluation.auto_test import *
from evaluation.parallel import parallel_worker
from generate_result import find_all_task_files
from evaluation.configs import AppConfig, TaskConfig

if __name__ == '__main__':
    # Default task-config list. Prefer ./evaluation/config (running from the
    # repository root); fall back to ../evaluation/config for the historical
    # working directory. Never raise before argparse: an eagerly-evaluated
    # default used to crash `python eval.py` outright.
    task_config_dir = None
    for _candidate in ("./evaluation/config", "../evaluation/config"):
        if os.path.isdir(_candidate):
            task_config_dir = _candidate
            break
    if task_config_dir is None:
        print("Warning: no 'evaluation/config' directory found; "
              "pass --task_config explicitly to select tasks.")
        task_yamls = []
    else:
        task_yamls = [os.path.join(task_config_dir, i)
                      for i in os.listdir(task_config_dir) if i.endswith(".yaml")]

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-n", "--name", default="test", type=str)
    arg_parser.add_argument("-c", "--config", default="config-mllm-0409.yaml", type=str)
    arg_parser.add_argument("--task_config", nargs="+", default=task_yamls, help="All task config(s) to load")
    arg_parser.add_argument("--task_id", nargs="+", default=None)
    arg_parser.add_argument("--debug", action="store_true", default=False)
    arg_parser.add_argument("--app", nargs="+", default=None)
    arg_parser.add_argument("-p", "--parallel", default=1, type=int)

    args = arg_parser.parse_args()
    # load_config expands ${ENV_VAR} placeholders (e.g. ${OPENROUTER_API_KEY});
    # configs without placeholders load exactly as before.
    yaml_data = load_config(args.config)

    agent_config = yaml_data["agent"]
    task_config = yaml_data["task"]
    eval_config = yaml_data["eval"]

    autotask_class = task_config["class"] if "class" in task_config else "ScreenshotMobileTask_AutoTest"

    single_config = TaskConfig(**task_config["args"])
    single_config = single_config.add_config(eval_config)
    if "True" == agent_config.get("relative_bbox"):
        single_config.is_relative_bbox = True

    # Resolve the task list before building the agent: a bad --task_config should
    # report itself instead of surfacing as a missing-API-key error first.
    task_files = find_all_task_files(args.task_config)
    if not task_files:
        # Fail here rather than constructing an Instance: that would clone an
        # AVD (and, in the app-map harness, boot an emulator) for zero tasks.
        raise SystemExit(
            "No task config files found. Pass --task_config with a path to a task "
            "config file or directory, e.g. --task_config evaluation/config/setting.yaml"
        )

    agent = get_agent(agent_config["name"], **agent_config["args"])

    if os.path.exists(os.path.join(single_config.save_dir, args.name)):
        already_run = os.listdir(os.path.join(single_config.save_dir, args.name))
        already_run = [i.split("_")[0] + "_" + i.split("_")[1] for i in already_run]
    else:
        already_run = []

    all_task_start_info = []
    for app_task_config_path in task_files:
        app_config = AppConfig(app_task_config_path)
        if args.task_id is None:
            task_ids = list(app_config.task_name.keys())
        else:
            task_ids = args.task_id
        for task_id in task_ids:
            if task_id in already_run:
                print(f"Task {task_id} already run, skipping")
                continue
            if task_id not in app_config.task_name:
                continue
            task_instruction = app_config.task_name[task_id].strip()
            app = app_config.APP
            if args.app is not None:
                print(app, args.app)
                if app not in args.app:
                    continue
            package = app_config.package
            command_per_step = app_config.command_per_step.get(task_id, None)

            task_instruction = f"You should use {app} to complete the following task: {task_instruction}"
            all_task_start_info.append({
                "agent": agent,
                "task_id": task_id,
                "task_instruction": task_instruction,
                "package": package,
                "command_per_step": command_per_step,
                "app": app
            })

    class_ = globals().get(autotask_class)
    if class_ is None:
        raise AttributeError(f"Class {autotask_class} not found. Please check the class name in the config file.")

    if args.parallel == 1:
        Auto_Test = class_(single_config.subdir_config(args.name))
        Auto_Test.run_serial(all_task_start_info)
    else:
        parallel_worker(class_, single_config.subdir_config(args.name), args.parallel, all_task_start_info)


