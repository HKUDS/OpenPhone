#!/usr/bin/env python3
"""Build an Android app map via ADB.

Two modes:
  1. Auto mode (default): clone AVD → start headless emulator → build → stop → cleanup
  2. Device mode (--device SERIAL): connect to an existing device, skip lifecycle

Usage:
    # Auto: clone + start + build + cleanup (default: headless)
    python build_android_map.py -p com.android.settings -a Settings

    # Show emulator window
    python build_android_map.py -p com.android.settings -a Settings --show-avd

    # Use existing device, no lifecycle management
    python build_android_map.py -p com.android.settings -a Settings --device emulator-5554

    # Read AVD settings from a test config YAML
    python build_android_map.py -p com.android.settings -a Settings -c configs/test_screen_react.yaml
"""

import argparse
import os
import subprocess
import shutil
import sys
import time

import yaml

from evaluation.build_map import build_app_map
from evaluation.utils import clone_avd, get_adb_device_name, list_all_devices, execute_adb
from utils_mobile.and_controller import AndroidController

from config_env import load_config


# ---------------------------------------------------------------------------
# Auto mode: emulator lifecycle (clone → start → stop → cleanup)
# ---------------------------------------------------------------------------

class BuildInstance:
    """Minimal Instance-like lifecycle for auto mode."""

    def __init__(self, avd_base, avd_name, avd_log_dir, show_avd=False, idx=0):
        self.idx = str(idx)
        self.avd_base = avd_base
        self.src_avd_name = avd_name
        self.avd_log_dir = avd_log_dir
        self.show_avd = show_avd
        self.emulator_process = None
        self.out_file = None
        self.tar_avd_dir = None
        self.tar_ini_file = None

    def clone(self):
        self.avd_name = f"{self.src_avd_name}_mapbuild_{self.idx}"
        print(f"Cloning AVD: {self.src_avd_name} → {self.avd_name}")
        self.tar_avd_dir, self.tar_ini_file = clone_avd(
            self.src_avd_name, self.avd_name, self.avd_base
        )

    def start(self):
        os.makedirs(self.avd_log_dir, exist_ok=True)
        self.out_file = open(
            os.path.join(self.avd_log_dir, f"emulator_mapbuild_{self.idx}.txt"), "w"
        )

        emu_args = ["emulator", "-avd", self.avd_name, "-no-snapshot-save"]
        if not self.show_avd:
            emu_args += ["-no-window", "-no-audio"]

        print(f"Starting emulator headless: {self.avd_name}")
        self.emulator_process = subprocess.Popen(
            emu_args, stdout=self.out_file, stderr=self.out_file
        )

        print("Waiting for device...")
        while True:
            try:
                device = get_adb_device_name(self.avd_name)
            except Exception:
                continue
            if device is not None:
                break

        print(f"Device: {device}")

        while True:
            boot = execute_adb(
                f"adb -s {device} shell getprop init.svc.bootanim", output=False
            )
            if boot == "stopped":
                print("Boot complete")
                break
            time.sleep(2)

        time.sleep(2)
        return device

    def stop(self):
        print("Stopping emulator...")
        if self.emulator_process:
            self.emulator_process.terminate()
            try:
                self.emulator_process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.emulator_process.kill()

        for _ in range(30):
            try:
                get_adb_device_name(self.avd_name)
            except Exception:
                break
            time.sleep(1)

        if self.out_file:
            self.out_file.close()

        if self.tar_avd_dir and os.path.exists(self.tar_avd_dir):
            shutil.rmtree(self.tar_avd_dir)
            print(f"Removed {self.tar_avd_dir}")
        if self.tar_ini_file and os.path.exists(self.tar_ini_file):
            os.remove(self.tar_ini_file)

        log_path = os.path.join(self.avd_log_dir, f"emulator_mapbuild_{self.idx}.txt")
        if os.path.exists(log_path):
            os.remove(log_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Build Android app map via ADB")
    parser.add_argument("--package", "-p", required=True, help="Android package name")
    parser.add_argument("--app", "-a", required=True, help="Human-readable app name")
    parser.add_argument("--output", "-o", default="./app_maps/app_map.yaml")
    parser.add_argument("--config", "-c", default=None,
                        help="YAML config file (same format as test configs)")
    parser.add_argument("--device", "-d", default=None,
                        help="Use existing device (skip emulator lifecycle)")
    parser.add_argument("--show-avd", action="store_true",
                        help="Show emulator GUI window (default: headless)")
    parser.add_argument("--avd-base", default=None,
                        help="AVD home dir (default: ~/.android/avd)")
    parser.add_argument("--avd-name", default=None,
                        help="Source AVD name (default: Pixel_7_Pro_API_33)")
    parser.add_argument("--max-screens", type=int, default=50)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--scroll-pages", type=int, default=3)
    parser.add_argument("--no-classify", action="store_true",
                        help="Disable LLM element classification")
    parser.add_argument("--no-enrich", action="store_true",
                        help="Disable LLM enrichment (aliases, descriptions)")
    parser.add_argument("--llm-api-key", default=None,
                        help="LLM API key for classification")
    parser.add_argument("--llm-api-base", default=None,
                        help="LLM API base URL for classification")
    parser.add_argument("--llm-model", default=None,
                        help="LLM model for classification")
    args = parser.parse_args()

    # Resolve config — CLI args take precedence over YAML config
    avd_base = args.avd_base
    avd_name = args.avd_name or "Pixel_7_Pro_API_33"
    avd_log_dir = "./logs/map_build"
    show_avd = args.show_avd

    if args.config:
        cfg = load_config(args.config)
        eval_cfg = cfg.get("eval", {})
        if not avd_base:
            avd_base = eval_cfg.get("avd_base")
        if not args.avd_name:
            avd_name = eval_cfg.get("avd_name", avd_name)
        if not avd_log_dir:
            avd_log_dir = eval_cfg.get("avd_log_dir", avd_log_dir)
        # show_avd is CLI-only — the config's show_avd is for testing, not map building
        agent_cfg = cfg.get("agent", {}).get("args", {})
        if not args.llm_api_key:
            args.llm_api_key = agent_cfg.get("api_key")
        if not args.llm_api_base:
            args.llm_api_base = agent_cfg.get("api_base")
        if not args.llm_model:
            args.llm_model = agent_cfg.get("model_name")

    # Resolve LLM config with defaults
    classify = not args.no_classify
    enrich = not args.no_enrich
    llm_api_key = args.llm_api_key or "EMPTY"
    llm_api_base = args.llm_api_base or "https://openrouter.ai/api/v1"
    llm_model = args.llm_model or "qwen/qwen3.7-plus"

    # -----------------------------------------------------------------------
    # Mode: existing device
    # -----------------------------------------------------------------------
    if args.device:
        print(f"Using existing device: {args.device}")
        controller = AndroidController(args.device)
        controller.run_command("adb root")
        time.sleep(1)
        print(f"Device size: {controller.width}x{controller.height}")

        output_path = build_app_map(
            controller=controller,
            package=args.package,
            app_name=args.app,
            output_path=args.output,
            max_screens=args.max_screens,
            max_depth=args.max_depth,
            scroll_pages=args.scroll_pages,
            classify=classify,
            enrich=enrich,
            llm_api_key=llm_api_key,
            llm_api_base=llm_api_base,
            llm_model=llm_model,
        )
        print(f"\nDone. App map saved to: {output_path}")
        return

    # -----------------------------------------------------------------------
    # Mode: auto (clone → start headless → build → stop → cleanup)
    # -----------------------------------------------------------------------
    if not avd_base:
        avd_base = os.path.expanduser("~/.android/avd")

    instance = BuildInstance(avd_base, avd_name, avd_log_dir, show_avd=show_avd)

    try:
        instance.clone()
        device = instance.start()

        controller = AndroidController(device)
        controller.run_command("adb root")
        time.sleep(1)
        print(f"Device size: {controller.width}x{controller.height}")

        output_path = build_app_map(
            controller=controller,
            package=args.package,
            app_name=args.app,
            output_path=args.output,
            max_screens=args.max_screens,
            max_depth=args.max_depth,
            scroll_pages=args.scroll_pages,
            classify=classify,
            enrich=enrich,
            llm_api_key=llm_api_key,
            llm_api_base=llm_api_base,
            llm_model=llm_model,
        )
        print(f"\nDone. App map saved to: {output_path}")

    finally:
        instance.stop()


if __name__ == "__main__":
    main()
