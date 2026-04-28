# EZSmolagents

EZSmolagents makes smolagents easy - a simplified API for running AI agents with LiteLLMModel using Docker isolation.

## Quick Start

```python
from easyrun import run_simple

result = run_simple("Write a Python script that fetches weather data", model="openai/gpt-4o-mini")
```

## Installation

```bash
pip install -e .
```

Requires Docker and a LiteLLM-compatible API key (e.g., OpenRouter).

## Features

- **Docker isolation**: Safe execution with configurable security levels
- **Multiple execution modes**: Docker (isolated) or local (development)
- **Streaming support**: Real-time output
- **Any LiteLLM model**: OpenAI, Anthropic, Google, etc.
- **Simple API**: Just import and run

## Usage

### Docker Execution (default)

```python
from easyrun import run_simple

result = run_simple(
    prompt="Write a Python script that fetches weather data",
    model="openai/gpt-4o-mini",
    api_key="your-api-key",
    security_level="standard"  # or "strict" / "relaxed"
)
```

### Streaming Execution

```python
from easyrun import run_simple_stream

for line in run_simple_stream("Write a report"):
    print(line, end="")
```

### Local Execution (no Docker)

```python
from easyrun import run_local

result = run_local("Debug this code", model="openai/gpt-4o-mini")
```

## Security Levels

| Level | Capabilities | Read-only FS | Network | Memory | CPU |
|-------|-------------|--------------|---------|--------|-----|
| `strict` | All dropped | Yes | Disabled | 512MB | 50% |
| `standard` | All dropped | No | Enabled | 1GB | 100% |
| `relaxed` | Minimal | No | Enabled | None | None |

## Custom Executor Scripts

You can also pass a custom executor script:

```python
result = run_simple(
    "Analyze the data",
    model="openai/gpt-4o",
    executor_path="/path/to/my_task.py"
)
```

Your script should define a `main(prompt, model)` or `run(prompt, model)` function.

## Setup

The Docker runner uses a custom image `ezsmolagents-runner:latest` with `smolagents[litellm]` pre-installed. Build it with:

```bash
docker build -t ezsmolagents-runner -f - . <<'EOF'
FROM python:3.13-slim
RUN pip install --no-cache-dir smolagents[litellm]>=1.24.0 docker>=7.1.0
EOF
```

Or use the pre-built image (if available).

## License

GNU Affero General Public License v3.0
