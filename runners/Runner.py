
class Runner():
    """Base class for all runners. Runners are responsible for running the agent and any isolation this tool provides."""
    def __init__(self,model,**kw) -> None:
        """Base class for all runners. Runners are responsible for running the agent and any isolation this tool provides."""
        self.model = model
        self.kw = kw
    def run(self):
        """Runs the agent. This method should be overridden by all subclasses. For DEBUG PURPOSES ONLY!!"""
        raise NotImplementedError("This method should be overridden by all subclasses.")


