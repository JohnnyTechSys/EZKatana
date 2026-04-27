#!/usr/bin/env python3
"""Executor script that runs inside the Docker container.
Uses LiteLLMModel for LLM interactions.
"""
import argparse
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model-id", default=None)
    parser.add_argument("--executor", required=True)
    args = parser.parse_args()

    # Add the ezsmolagents package to path
    pkg_root = "/mnt/ezsmolagents"
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)

    # Import LiteLLMModel
    from smolagents.models import LiteLLMModel

    # Create model instance
    model_id = args.model_id or os.environ.get("EZSMOLAGENTS_MODEL_ID", "openai/gpt-4o-mini")
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = LiteLLMModel(model_id=model_id, api_key=api_key)

    # Load and execute the user's executor script
    executor_path = Path(args.executor)
    if not executor_path.exists():
        print(f"Executor not found: {executor_path}", file=sys.stderr)
        sys.exit(1)

    # Execute the user's script in its own context
    import importlib.util
    spec = importlib.util.spec_from_file_location("user_executor", executor_path)
    module = importlib.util.module_from_spec(spec)

    # Set up module globals with helpful context
    module.__dict__["__agent_prompt"] = args.prompt
    module.__dict__["__agent_model"] = model
    module.__dict__["__agent_model_id"] = model_id

    try:
        spec.loader.exec_module(module)
        # Look for a main function or similar entry point
        if hasattr(module, "main"):
            result = module.main(args.prompt, model)
            if result is not None:
                print(result)
        elif hasattr(module, "run"):
            result = module.run(args.prompt, model)
            if result is not None:
                print(result)
        else:
            # Just execute and hope for side effects
            print(f"Executing {executor_path.name} with prompt: {args.prompt}")
            print(f"Model: {model_id}")
    except Exception as e:
        print(f"Executor error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
