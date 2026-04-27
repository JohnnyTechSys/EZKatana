"""Easy-to-use API for running ezsmolagents.

This module provides simplified entry points for running agents with LiteLLMModel.
Can be used either with Docker isolation or local execution.

Supports running as a standalone script or as an imported module.
"""
import sys
import os
from pathlib import Path
import inspect

# Compute importer_filename like __init__.py does
def get_importer_filename():
    for frame_info in inspect.stack():
        fname = frame_info.filename
        if "_bootstrap" not in fname and fname != __file__:
            return fname
    return None

importer_filename = get_importer_filename()

# Import runners directly (no package-relative imports)
try:
    from runners.DockerRunner import DockerRunnerFrontend
    from runners.LocalRunner import LocalRunnerFrontend
except ImportError as e:
    print(f"Error importing runners: {e}", file=sys.stderr)
    sys.exit(1)

from rich import print as rprint
from rich.console import Console

console = Console()


def run_simple(prompt: str, model=None, api_key: str = None, security_level: str = "standard", **kw):
    """Simplified entry point for running agents in Docker with LiteLLMModel.

    Args:
        prompt: The task/prompt for the agent
        model: LiteLLMModel instance or model_id string (e.g. "openai/gpt-4o-mini")
               Defaults to "openai/gpt-4o-mini"
        api_key: Optional API key (passed to LiteLLMModel)
        security_level: "strict", "standard", or "relaxed"
        **kw: Additional kwargs passed to Docker runner

    Returns:
        Output from agent execution (str)
    """
    runner = DockerRunnerFrontend(
        model=model,
        executor_path=importer_filename,
        api_key=api_key,
        security_level=security_level,
        **kw
    )
    result = runner.run(prompt, stream=False)
    rprint(result)
    return result


def run_simple_stream(prompt: str, model=None, api_key: str = None, security_level: str = "standard", **kw):
    """Streaming version of run_simple.

    Yields lines from container output as they become available.
    """
    runner = DockerRunnerFrontend(
        model=model,
        executor_path=importer_filename,
        api_key=api_key,
        security_level=security_level,
        **kw
    )
    for line in runner.run(prompt, stream=True):
        console.print(line)
        yield line


def run_local(prompt: str, model=None, api_key: str = None, python_executable: str = None, **kw):
    """Run agent locally (no Docker isolation) with LiteLLMModel.

    Args:
        prompt: The task/prompt for the agent
        model: LiteLLMModel instance or model_id string
               Defaults to "openai/gpt-4o-mini"
        api_key: Optional API key
        python_executable: Python interpreter to use (defaults to current interpreter)
        **kw: Additional kwargs passed to Local runner

    Returns:
        Output from agent execution
    """
    runner = LocalRunnerFrontend(
        model=model,
        executor_path=importer_filename,
        api_key=api_key,
        python_executable=python_executable,
        **kw
    )
    result = runner.run(prompt, stream=False)
    rprint(result)
    return result


def run_local_stream(prompt: str, model=None, api_key: str = None, python_executable: str = None, **kw):
    """Streaming version of local execution.

    Yields lines from execution output as they become available.
    """
    runner = LocalRunnerFrontend(
        model=model,
        executor_path=importer_filename,
        api_key=api_key,
        python_executable=python_executable,
        **kw
    )
    for line in runner.run(prompt, stream=True):
        console.print(line)
        yield line


if __name__ == "__main__":
    print("EZSmolagents Easy Run")
    print("Use functions like run_simple() or run_local() to execute agents.")
