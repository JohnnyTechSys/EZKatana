# EZSmolagents - Application Overview

**EZSmolagents** is a streamlined Python framework designed to make `smolagents` (by Hugging Face) easy to use with robust isolation. It specializes in running AI agents using the `LiteLLMModel` backend with built-in support for Docker-based sandboxing.

## Architecture

The project is structured to separate the high-level user API from the low-level execution logic:

```
ezsmolagents/
├── easyrun.py                 # Convenience API (run_simple, run_local, etc.)
├── __init__.py               # Package exports, path utilities, and easter egg
├── __main__.py               # Entry point (primarily displays license/branding)
├── pyproject.toml            # Project metadata and dependencies
├── runners/
│   ├── Runner.py             # Abstract base class for all runners
│   ├── DockerRunner.py       # Docker-based isolated execution (Backend + Frontend)
│   ├── LocalRunner.py        # Subprocess-based local execution (Backend + Frontend)
│   └── container_executor.py # The script that orchestrates the agent inside the container
└── README.md                 # User-facing documentation and quick start
```

## Core Components

### 1. Runner Hierarchy (`runners/`)
The system uses a "Frontend/Backend" pattern to separate runner configuration from execution:
- **`Runner` (Base)**: An abstract interface requiring a `run(prompt, stream)` method.
- **`DockerRunner`**: 
    - **Backend**: Manages Docker volumes, container lifecycle, and resource constraints.
    - **Frontend**: Handles high-level configuration like security levels and API keys.
- **`LocalRunner`**: 
    - **Backend**: Executes the agent in a local subprocess.
    - **Frontend**: Injects environment variables and manages local paths.

### 2. Convenience API (`easyrun.py`)
Provides "one-liner" access to the framework without needing to instantiate runner classes manually:
- `run_simple()`: The standard entry point for Docker-isolated execution.
- `run_simple_stream()`: Streaming version of Docker execution.
- `run_local()` / `run_local_stream()`: Non-isolated execution for development and debugging.

### 3. Container Orchestration (`runners/container_executor.py`)
When running in Docker, this script is the internal entry point. It:
1. Dynamically loads the user's executor script.
2. Injects critical globals like `__agent_prompt`, `__agent_model`, and `__agent_model_id`.
3. Looks for a `main()` or `run()` function in the user script to trigger the agent.

### 4. Security Sandboxing
The `DockerRunner` implements three distinct security profiles:
- **`strict`**: Maximum isolation (Read-only FS, No Network, 512MB RAM).
- **`standard`**: Balanced (Network enabled, 1GB RAM).
- **`relaxed`**: Minimal restrictions (Resource limits removed).

## Key Implementation Details

### Importer Path Resolution
The framework uses `inspect.stack()` in `__init__.py` to automatically detect the file that called it. This allows `run_simple()` to "magically" find and package the user's current script into the Docker container without requiring explicit paths in most cases.

### Streaming Architecture
Execution logs are streamed from the Docker/Subprocess backend using generators. The `DockerRunner` is carefully implemented to return a string for standard calls and a generator for streaming calls, ensuring type consistency for the user.

### Dependencies
- **smolagents[litellm]**: The core agent logic and multi-provider LLM support.
- **docker**: For container management.
- **rich**: For beautiful terminal output and inspection.
- **setuptools/uv**: For package management.
