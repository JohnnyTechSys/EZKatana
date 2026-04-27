from .Runner import Runner
import docker
from pathlib import Path
from uuid import uuid4
try:
    from ..__init__ import get_paths_for_required_package_files
except ImportError:
    # Fallback for direct file execution - compute manually
    import os
    def get_paths_for_required_package_files():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


class DockerRunnerBackend(Runner):
    """Docker runner that executes agents in isolated containers using LiteLLMModel."""
    def __init__(self, executor_path=None, override_container_name=None, model=None, api_key=None, security_level="standard", **kw):
        from smolagents.models import LiteLLMModel
        if isinstance(model, str) or model is None:
            model_id = model or "openai/gpt-4o-mini"
            model = LiteLLMModel(model_id=model_id, api_key=api_key)
        super().__init__(model, **kw)
        self.client = docker.from_env()
        self.container_name = str(uuid4()) if override_container_name is None else override_container_name
        if executor_path is None:
            raise ValueError("executor_path is required for DockerRunner.")
        self.executor_path = Path(executor_path).resolve()
        self.api_key = api_key
        self.security_level = security_level
        if not self.executor_path.exists():
            raise FileNotFoundError(f"Executor script not found: {self.executor_path}")

    def _get_security_config(self):
        cfg = {"cap_drop": [], "read_only": False, "network_disabled": False, "mem_limit": None, "cpu_quota": None}
        if self.security_level == "strict":
            cfg["cap_drop"] = ["ALL"]
            cfg["read_only"] = True
            cfg["network_disabled"] = True
            cfg["mem_limit"] = "512m"
            cfg["cpu_quota"] = 50000
        elif self.security_level == "standard":
            cfg["cap_drop"] = ["ALL"]
            cfg["mem_limit"] = "1g"
            cfg["cpu_quota"] = 100000
        return cfg

    def run(self, prompt, stream=False):
        pkgroot = get_paths_for_required_package_files()
        executor_parent = str(self.executor_path.parent)
        volumes = {
            pkgroot: {"bind": "/mnt/ezsmolagents", "mode": "ro"},
            executor_parent: {"bind": "/workspace", "mode": "rw"}
        }
        sec = self._get_security_config()
        env = {
            "EZSMOLAGENTS_PROMPT": prompt,
            "EZSMOLAGENTS_MODEL_ID": getattr(self.model, 'model_id', str(self.model)),
        }
        if self.api_key:
            env["OPENROUTER_API_KEY"] = self.api_key
        try:
            container = self.client.containers.run(
                "python:3.13-slim", name=str(self.container_name),
                command=["python", "-u", "/mnt/ezsmolagents/runners/container_executor.py",
                         "--prompt", prompt,
                         "--executor", f"/workspace/{self.executor_path.name}"],
                volumes=volumes, environment=env, working_dir="/workspace",
                detach=True, remove=True, cap_drop=sec["cap_drop"],
                read_only=sec["read_only"], network_disabled=sec["network_disabled"],
                mem_limit=sec["mem_limit"], cpu_quota=sec["cpu_quota"],
            )
            if stream:
                for line in container.logs(stream=True, follow=True):
                    yield line.decode("utf-8").rstrip("\n")
            else:
                result = container.wait()
                logs = container.logs().decode("utf-8")
                if result["StatusCode"] != 0:
                    raise RuntimeError(f"Container failed: {result['StatusCode']}\n{logs}")
                return logs
        except docker.errors.ContainerError as e:
            raise RuntimeError(f"Container error: {e}")
        except docker.errors.ImageNotFound:
            raise RuntimeError("Python 3.13-slim image not found.")


class DockerRunnerFrontend(Runner):
    def __init__(self, executor_path=None, override_container_name=None, model=None, api_key=None, security_level="standard", **kw):
        super().__init__(model, **kw)
        self.backend = DockerRunnerBackend(
            executor_path=executor_path, override_container_name=override_container_name,
            model=model, api_key=api_key, security_level=security_level, **kw)
    def run(self, prompt, stream=False):
        return self.backend.run(prompt, stream=stream)
