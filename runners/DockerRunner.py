from .Runner import Runner
import docker
import os
from uuid import uuid4
from ..__init__ import get_paths_for_required_package_files
class DockerRunnerBackend(Runner):
    """DockerRunner is a runner that runs the agent in a Docker container. It uses the docker Python package to manage the container."""
    def __init__(self,model,override_container_name=None,**kw):
        """DockerRunner is a runner that runs the agent in a Docker container. It uses the docker Python package to manage the container."""
        super().__init__(model,**kw)
        self.client = docker.from_env()
        self.container = uuid4() if override_container_name is None else override_container_name
    def run(self):
        pkgroot = get_paths_for_required_package_files()
        volumes = {
        pkgroot: {
            'bind': '/mnt/ezsmolagents',
            'mode': 'ro'  # or 'ro' for read-only
        }
    }
        
        
