import os
import sys
from rich import print
from rich.console import Console
from rich.prompt import Prompt

# Prevent the script from running its own CLI logic if it's being executed 
# as the "task" inside the Docker container.
if os.environ.get("EZSMOLAGENTS_PROMPT"):
    import logging
    import warnings
    
    # Silence all the noise
    logging.getLogger("smolagents").setLevel(logging.ERROR)
    logging.getLogger("litellm").setLevel(logging.ERROR)
    warnings.filterwarnings("ignore")
    os.environ["LITELLM_LOG"] = "ERROR"

    from smolagents import CodeAgent
    from smolagents.models import LiteLLMModel
    
    def main(prompt, model):
        """This is the entry point called inside the container."""
        # Ensure the model uses the host-gateway if it's ollama
        if hasattr(model, "api_base") and "ollama" in str(getattr(model, "model_id", "")).lower():
             model.api_base = "http://host.docker.internal:11434"

        # verbosity_level=0 is key to removing banners
        agent = CodeAgent(tools=[], model=model, verbosity_level=0)
        
        # We manually iterate and only print content to avoid any library-level formatting
        try:
            for message in agent.run(prompt, stream=True):
                # We only care about Final Answer or actual content
                if hasattr(message, 'content') and message.content:
                    sys.stdout.write(str(message.content))
                    sys.stdout.flush()
                elif isinstance(message, str):
                    sys.stdout.write(message)
                    sys.stdout.flush()
        except Exception as e:
            # Print only the core error message to avoid traceback noise in CLI
            sys.stderr.write(f"\nError: {str(e)}\n")
            sys.exit(1)
    
    if __name__ == "__main__":
        pass 
else:
    # This is the local CLI logic
    from .easyrun import run_simple, run_simple_stream

    console = Console()

    def start_cli():
        console.print("[bold magenta]EZSmolagents CLI[/bold magenta]")
        
        model_id = Prompt.ask(
            "Enter the LiteLLM model code", 
            default="ollama/gemma3:1b"
        )
        
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key and "ollama" not in model_id:
            api_key = Prompt.ask("Enter your API Key", password=True)

        while True:
            try:
                prompt = Prompt.ask("\n[bold green]Ask the AI Agent[/bold green] (or 'exit' to quit)")
                
                if prompt.lower() in ["exit", "quit"]:
                    break
                
                console.print(f"[blue]Sent to {model_id}:[/blue] {prompt}\n")
                
                # Stream directly to stdout for the cleanest experience
                for line in run_simple_stream(
                    prompt, 
                    model=model_id, 
                    api_key=api_key
                ):
                    # run_simple_stream prints each line
                    pass
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")

    if __name__ == "__main__":
        choice = Prompt.ask(
            "Continue in the Web UI or CLI?", 
            choices=["Web UI", "CLI"],
            default="Web UI"
        )
        
        if choice == "Web UI":
            print("[red underline]Web UI is not implemented yet. Starting CLI instead...[/red underline]")
            start_cli()
        else:
            start_cli()
