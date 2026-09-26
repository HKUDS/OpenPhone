"""Run the judge evaluator on existing agent traces to get real scores.

Usage:
    # With API key from env var (for LLM judge tasks)
    API_KEY=sk-... python run_eval_judge.py --traces logs/evaluation/macro_v8 --config evaluation/config/setting.yaml

    # With API key from test config file
    python run_eval_judge.py --traces logs/evaluation/macro_v8 --config evaluation/config/setting.yaml --test-config configs/test_macro.yaml

    # With explicit API key
    python run_eval_judge.py --traces logs/evaluation/macro_v8 --config evaluation/config/setting.yaml --api-key sk-... --api-base https://openrouter.ai/api/v1
"""
import sys, os, json, argparse
from config_env import load_config
from evaluation.configs import AppConfig
from evaluation.task import Evaluation_Task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", required=True, help="Path to trace root directory")
    parser.add_argument("--config", required=True, help="Path to task config YAML")
    parser.add_argument("--test-config", default=None,
                        help="Path to test config YAML (reads api_key/api_base from agent section)")
    parser.add_argument("--api-key", default=None, help="API key for LLM judge")
    parser.add_argument("--api-base", default=None, help="API base URL for LLM judge")
    parser.add_argument("--model", default=None, help="Model name for LLM judge")
    parser.add_argument("--detail", action="store_true", default=False)
    args = parser.parse_args()

    # Resolve API credentials: CLI args > test config > auto-discover > env vars
    api_key = args.api_key
    api_base = args.api_base
    model = args.model

    # Try explicit --test-config first
    if args.test_config and (not api_key or not api_base):
        cfg = load_config(args.test_config)
        agent_cfg = cfg.get("agent", {}).get("args", {})
        if not api_key:
            api_key = agent_cfg.get("api_key")
        if not api_base:
            api_base = agent_cfg.get("api_base")
        if not model:
            model = agent_cfg.get("model_name")

    # Auto-discover: scan configs/test_*.yaml for API credentials
    if not api_key or not api_base:
        import glob
        for cfg_path in sorted(glob.glob("configs/test_*.yaml")):
            try:
                cfg = load_config(cfg_path)
                agent_cfg = cfg.get("agent", {}).get("args", {})
                if not api_key:
                    api_key = agent_cfg.get("api_key")
                if not api_base:
                    api_base = agent_cfg.get("api_base")
                if not model:
                    model = agent_cfg.get("model_name")
                if api_key and api_key != "EMPTY":
                    break
            except Exception:
                pass

    # Set env vars so LLMEvaluator picks them up
    if api_key:
        os.environ["API_KEY"] = api_key
    if api_base:
        os.environ["API_BASE"] = api_base
    if model:
        os.environ["MODEL_NAME"] = model

    if api_key:
        print(f"Using API key (from {'CLI' if args.api_key else 'config'}): {api_key[:20]}...")
    else:
        print("WARNING: No API key provided — LLM judge will fall back to programmatic checks")

    # Load task config with output dir set to traces directory
    config = AppConfig(args.config, output_dir=args.traces)

    # Build traces dict from the trace directory
    traces = {}
    for task_dir in sorted(os.listdir(args.traces)):
        trace_dir = os.path.join(args.traces, task_dir)
        trace_file = os.path.join(trace_dir, "traces", "trace.jsonl")
        xml_path = os.path.join(trace_dir, "xml")
        if not os.path.isfile(trace_file):
            continue
        parts = task_dir.split("_")
        task_id = f"{parts[0]}_{parts[1]}"
        traces[task_id] = {
            "task_id": task_id,
            "trace_file": trace_file,
            "xml_path": xml_path,
            "trace_root": trace_dir,
        }

    print(f"Loaded {len(traces)} traces from {args.traces}")
    print(f"Task config: {config.APP} ({config.package}), {len(config.get_tasks())} tasks")

    # Run evaluation
    class FakeArgs:
        pass
    fake_args = FakeArgs()
    evaluator = Evaluation_Task(config, traces, fake_args, detail=args.detail)
    evaluator.evaluate()


if __name__ == "__main__":
    main()
