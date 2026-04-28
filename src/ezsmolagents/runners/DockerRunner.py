from .Runner import Runner
import docker
from pathlib import Path
from uuid import uuid4
import warnings
try:
    from ..__init__ import get_paths_for_required_package_files
except ImportError:
    import os
    def get_paths_for_required_package_files():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


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

        # Handle case where package root and executor parent are the same directory
        # Docker SDK can't mount the same host dir twice with different destinations
        if pkgroot == executor_parent:
            volumes = {
                pkgroot: {"bind": "/mnt/ezsmolagents", "mode": "rw"}
            }
            container_executor_path = "/mnt/ezsmolagents/runners/container_executor.py"
            executor_container_path = f"/mnt/ezsmolagents/{self.executor_path.name}"
            working_dir = "/mnt/ezsmolagents"
        else:
            volumes = {
                pkgroot: {"bind": "/mnt/ezsmolagents", "mode": "ro"},
                executor_parent: {"bind": "/workspace", "mode": "rw"}
            }
            container_executor_path = "/mnt/ezsmolagents/runners/container_executor.py"
            executor_container_path = f"/workspace/{self.executor_path.name}"
            working_dir = "/workspace"

        sec = self._get_security_config()
        
        # If using Ollama, we need to reach the host's server.
        # host.docker.internal is the most reliable way across platforms.
        extra_hosts = {"host.docker.internal": "host-gateway"}
        
        env = {
            "EZSMOLAGENTS_PROMPT": prompt,
            "EZSMOLAGENTS_MODEL_ID": getattr(self.model, 'model_id', str(self.model)),
            "LITELLM_LOG": "ERROR",
            "SMOLAGENTS_LOG": "ERROR",
            "PYTHONUNBUFFERED": "1",
        }
        
        # If it's Ollama, tell LiteLLM where to look
        if "ollama" in str(getattr(self.model, 'model_id', '')).lower():
            env["OLLAMA_API_BASE"] = "http://host.docker.internal:11434"

        if self.api_key:
            env["OPENROUTER_API_KEY"] = self.api_key
        try:
            container = self.client.containers.run(
                "ezsmolagents-runner:latest", name=str(self.container_name),
                command=["python", "-u", container_executor_path,
                         "--prompt", prompt,
                         "--executor", executor_container_path],
                volumes=volumes, environment=env, working_dir=working_dir,
                detach=True, remove=True, cap_drop=sec["cap_drop"],
                read_only=sec["read_only"], network_disabled=sec["network_disabled"],
                extra_hosts=extra_hosts,
                mem_limit=sec["mem_limit"], cpu_quota=sec["cpu_quota"],
            )
            if stream:
                def _stream():
                    for line in container.logs(stream=True, follow=True):
                        yield line.decode("utf-8").rstrip("\n")
                return _stream()
            else:
                result = container.wait()
                logs = container.logs().decode("utf-8")
                if result["StatusCode"] != 0:
                    raise RuntimeError(f"Container failed: {result['StatusCode']}\n{logs}")
                return logs
        except docker.errors.ContainerError as e:
            raise RuntimeError(f"Container error: {e}")
        except docker.errors.ImageNotFound:
            raise RuntimeError("ezsmolagents-runner:latest image not found. Build it with: docker build -t ezsmolagents-runner -f - . <<'EOF'\nFROM python:3.13-slim\nRUN pip install --no-cache-dir smolagents[litellm]>=1.24.0 docker>=7.1.0\nEOF")


class DockerRunnerFrontend(Runner):
    def __init__(self, executor_path=None, override_container_name=None, model=None, api_key=None, security_level="standard", **kw):
        from smolagents.models import LiteLLMModel
        if isinstance(model, str) or model is None:
            model_id = model or "openai/gpt-4o-mini"
            model = LiteLLMModel(model_id=model_id, api_key=api_key)
        super().__init__(model, **kw)
        self.backend = DockerRunnerBackend(
            executor_path=executor_path, override_container_name=override_container_name,
            model=model, api_key=api_key, security_level=security_level, **kw)
    def run(self, prompt, stream=False):
        return self.backend.run(prompt, stream=stream)
