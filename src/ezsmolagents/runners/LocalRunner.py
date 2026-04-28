from .Runner import Runner
import subprocess
import sys
import os
from pathlib import Path


class LocalRunner(Runner):
    """Local runner executing agents directly using LiteLLMModel (no Docker isolation).
    
    Useful for debugging and development where Docker is not available.
    """
    def __init__(self, executor_path=None, model=None, api_key=None, python_executable=None, **kw):
        from smolagents.models import LiteLLMModel
        if isinstance(model, str) or model is None:
            model_id = model or "openai/gpt-4o-mini"
            model = LiteLLMModel(model_id=model_id, api_key=api_key)
        super().__init__(model, **kw)
        if executor_path is None:
            raise ValueError("executor_path is required for LocalRunner.")
        self.executor_path = Path(executor_path).resolve()
        self.api_key = api_key
        self.python_executable = python_executable or sys.executable
        if not self.executor_path.exists():
            raise FileNotFoundError(f"Executor script not found: {self.executor_path}")

    def run(self, prompt, stream=False):
        """Run the executor script locally.
        
        Args:
            prompt: The task prompt to execute
            stream: If True, yields output lines as they become available.
                   If False, returns complete output as string.
        """
        env = os.environ.copy()
        env["EZSMOLAGENTS_PROMPT"] = prompt
        env["EZSMOLAGENTS_MODEL_ID"] = getattr(self.model, 'model_id', str(self.model))
        if self.api_key:
            env["OPENROUTER_API_KEY"] = self.api_key
        
        cmd = [self.python_executable, str(self.executor_path), "--prompt", prompt]
        
        if stream:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=env, text=True, bufsize=1, universal_newlines=True,
            )
            for line in iter(proc.stdout.readline, ''):
                if line:
                    yield line.rstrip('\n')
            proc.stdout.close()
            stderr_output = proc.stderr.read()
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"Local execution failed with code {proc.returncode}:\n{stderr_output}")
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            if result.returncode != 0:
                raise RuntimeError(f"Local execution failed with code {result.returncode}:\n{result.stderr}")
            return result.stdout


class LocalRunnerFrontend(Runner):
    """User-facing local runner with simplified interface."""
    def __init__(self, executor_path=None, model=None, api_key=None, python_executable=None, **kw):
        from smolagents.models import LiteLLMModel
        # Convert model to LiteLLMModel before storing (for type consistency)
        if isinstance(model, str) or model is None:
            model_id = model or "openai/gpt-4o-mini"
            model = LiteLLMModel(model_id=model_id, api_key=api_key)
        super().__init__(model, **kw)
        self.backend = LocalRunner(
            executor_path=executor_path, model=model, api_key=api_key,
            python_executable=python_executable, **kw)
    def run(self, prompt, stream=False):
        return self.backend.run(prompt, stream=stream)
