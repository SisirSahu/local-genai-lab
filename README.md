# Local GenAI Lab

A learning project built with Python, FastAPI, LangChain's Ollama integration,
and your locally downloaded `qwen3:8b` model. No cloud API key is required.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Python 3.11 (`uv` can install it if necessary)
- Ollama running locally with `qwen3:8b` downloaded (`ollama list` to check)

## Setup

Run commands from this project directory:

```bash
cd local-genai-lab
uv sync --locked
```

If this fails with a certificate error such as `UnknownIssuer`, use
`UV_NATIVE_TLS=true uv sync --locked` instead. This is network-dependent, not a
requirement for every installation; see [TLS and proxies](#tls-and-proxies).

If `.env` does not already exist, copy `.env.example` to `.env`. Confirm your
downloaded model with `ollama list`. To download it if missing:

```bash
ollama pull qwen3:8b
```

The model stays on disk across runs and restarts. Loading it into memory is not
another download. LangChain reports an error if the model is missing; it does not
download it automatically.

Choose any of the following ways to use the project; FastAPI is optional for
scripts and notebooks.

## Run a normal Python file

Save this example as `example.py` in the project root:

```python
from langchain_ollama import ChatOllama

model = ChatOllama(
    model="qwen3:8b",
    reasoning=False,
    client_kwargs={"trust_env": False},  # Bypass proxies for local Ollama.
)

response = model.invoke("Explain agentic AI in simple words.")
print(response.content)
```

Run it using the project's environment:

```bash
uv run python example.py
```

No FastAPI server or browser is needed; Ollama must still be running.
This standalone example uses explicit settings rather than loading `.env`.

Alternatively, activate the environment and run Python directly:

```bash
source .venv/bin/activate
python example.py
deactivate
```

### Imports and package modules

Both installed dependencies and your own project modules can be imported:

```python
from langchain_ollama import ChatOllama
from genai_app.config import get_settings
from genai_app.services.chat import ChatService
```

`uv sync` installs this project in editable mode, so Python finds `genai_app`
inside `src/` and sees source changes without reinstalling. No `sys.path` edits
or `PYTHONPATH` configuration are needed.

For a runnable module you create inside the package, use its dotted name:

```bash
# Example: after creating src/genai_app/example.py
uv run python -m genai_app.example
```

This also supports package-relative imports. Prefer `-m` over running a package
file by its filesystem path. A module only does what its top-level code or entry
point implements; running the FastAPI application module with Python alone does
not start an HTTP server.

## Run the FastAPI backend

```bash
uv run uvicorn genai_app.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://localhost:8000/docs for interactive API documentation.
Expand `POST /api/chat`, click **Try it out**, and submit:

```json
{"prompt": "Explain AI agents in three short sentences."}
```

Or use a terminal:

```bash
curl --noproxy '*' http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Explain AI agents in three short sentences."}'
```

Response shape:

```json
{"model": "qwen3:8b", "response": "The generated answer appears here."}
```

`GET /health` checks application liveness only; a successful chat checks the
complete Ollama path. The first request may take longer while the model loads
into memory.

## VS Code and notebooks

For **Run Python File**, use **Python: Select Interpreter** and choose this
project's `.venv/bin/python`, not a global Python installation.

For notebooks, use **Select Kernel > Python Environments** and select the same
project environment (Python 3.11). Notebook kernel selection is separate from the
editor's interpreter selection.

The development dependencies include `ipykernel`, which VS Code needs to execute
cells. If VS Code reports it missing, run `uv sync --locked`, reselect the project
kernel, and restart the kernel. No global Jupyter installation or manual kernel
registration is required. Notebook cells can import installed dependencies and
`genai_app` just like normal scripts.

## Dependencies: uv, pip, and requirements.txt

| File or directory | Purpose | Spring/Maven analogy |
|---|---|---|
| `pyproject.toml` | Project metadata, dependencies, and tool settings | `pom.xml` |
| `uv.lock` | Exact resolved versions, including transitive dependencies | Reproducible dependency resolution |
| `.python-version` | Python version selected by uv | JDK version selection |
| `.venv/` | Isolated Python environment and installed packages | No direct equivalent |
| `src/genai_app/` | Application package | `src/main/java` |
| `tests/` | Automated tests | `src/test/java` |

```bash
uv sync --locked             # Install the locked dependencies, including dev tools
uv add package-name          # Add a runtime dependency
uv add --dev package-name    # Add a development dependency
uv remove package-name       # Remove a runtime dependency
```

### Useful uv commands

Run these from the project root:

| Command | Purpose |
|---|---|
| `uv sync --locked` | Create/sync `.venv` using the existing lockfile; fail if it needs updating |
| `uv sync` | Sync the environment and update the lockfile if required |
| `uv add package-name` | Add, lock, and install a runtime dependency |
| `uv add --dev package-name` | Add, lock, and install a development dependency |
| `uv remove --dev package-name` | Remove a development dependency |
| `uv run python example.py` | Run a script in the project environment |
| `uv run python -m genai_app.example` | Run a package module you have created |
| `uv tree` | Show the dependency tree |
| `uv lock --check` | Check whether the lockfile matches the project metadata |
| `uv lock --upgrade-package package-name` | Update one package in the lockfile within declared constraints; run `uv sync --locked` afterward |
| `uv python list --only-installed` | List locally available Python interpreters |

`uv sync` and `uv run` manage the project environment automatically; manual
activation and a separate `uv venv` step are normally unnecessary.

### Recreate the virtual environment

After moving/renaming the project, or when the environment is broken, stop
running servers and notebook kernels and recreate **only this project's `.venv`**:

```bash
# Run from the project root; this replaces the existing .venv.
uv venv .venv
uv sync --locked
```

Recreation removes packages from the old environment, but does not remove source
files or the lockfile. Sync restores the declared dependencies. Then reselect the
interpreter/notebook kernel in VS Code. If a shell has the old environment
activated, run `deactivate` before recreation.

You may also see `uv venv --clear` in examples. The installed uv version accepts
it for compatibility but warns that it has no effect: `uv venv` already clears
the target environment unless `--allow-existing` is used. It is not needed here.

### Export requirements.txt

Some Python projects instead list dependencies in `requirements.txt` and install
them using `pip install -r requirements.txt`. This project does not need that
file: `pyproject.toml` and `uv.lock` already manage dependencies.

If a deployment platform needs `requirements.txt`, export it from the lockfile:

```bash
uv export --format requirements-txt --no-dev --no-emit-project \
  --output-file requirements.txt
```

Remove `--no-dev` to include development packages such as pytest and ipykernel.
The exported file excludes this project's own package, so it installs dependencies
only; the application must still be installed or its source made available in the
target environment.

Keep `pyproject.toml` as the source of truth and regenerate exports rather than
maintaining two dependency lists manually. Commit `pyproject.toml`, `uv.lock`,
and `.python-version`; do not commit `.venv/` or `.env`.

## Configuration

Settings are validated in [config.py](src/genai_app/config.py). Environment
variables override values in `.env`; `.env` is ignored by Git.

| Variable | Default | Meaning |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `qwen3:8b` | Already-downloaded model to use |
| `OLLAMA_TIMEOUT_SECONDS` | `120` | HTTP timeout per operation, in seconds |
| `LOG_LEVEL` | `INFO` | Application logging level |

### TLS and proxies

Ollama requests bypass environment proxies to keep local model traffic direct.
Do not store credentials or secrets in source control.

If dependency downloads fail because your network uses a custom certificate
authority, try the system certificate trust store:

```bash
UV_NATIVE_TLS=true uv sync --locked
```

This keeps certificate verification enabled. No system-wide proxy or certificate
settings are changed by this project. The prefix applies only to that command;
it can also be used with `uv add`, `uv lock`, or other uv commands that download
packages. Cached dependencies may let a sync succeed without a network request,
so a successful cached sync does not prove that TLS configuration is unnecessary.

If your network consistently requires the system trust store, enable it for the
current terminal session:

```bash
export UV_NATIVE_TLS=true
uv sync --locked
```

Putting this variable in the application's `.env` does not automatically
configure uv. Do not disable certificate verification to work around TLS errors.

If your network requires a proxy, configure `HTTP_PROXY`, `HTTPS_PROXY`, and
`NO_PROXY` in your shell using your network's settings. Include `localhost`,
`127.0.0.1`, and `::1` in `NO_PROXY`. Do not commit proxy addresses or credentials.
The application's `.env` is not a shell startup file, and `.python-version`
contains only the Python version.

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Normal tests use mocked model calls and do not require Ollama. To run the
end-to-end chat smoke test against the real model:

```bash
RUN_LIVE_TESTS=1 uv run pytest tests/integration/test_live_ollama.py -v
```

## Layout

- [src/genai_app/main.py](src/genai_app/main.py): application startup and health
- [api](src/genai_app/api/): HTTP routes and explicit upstream error handling
- [schemas](src/genai_app/schemas/): validated request and response models
- [services](src/genai_app/services/): asynchronous Ollama model calls
- [tests](tests/): unit tests, API tests, and an opt-in live test

## Scope and next steps

Chat is currently stateless: each request is independent. Output is non-streaming,
limited to 512 generated tokens, and Qwen thinking is disabled for a simple
starting experience. Prompts are limited to 16,000 characters, not tokens.
Timeouts return HTTP 504, connection failures 503, and model errors 502.

Next, add streaming, conversation persistence, then tool-calling agents and RAG.
Authentication and rate limiting are not implemented; keep this development
server bound to localhost and do not expose it publicly.
