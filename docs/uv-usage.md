# uv Usage Guide

Quick reference for using uv in this project.

## First Time Setup

After cloning the repo, create the virtual environment and install dependencies:

```bash
# 1. Create the virtual environment
uv venv --python 3.12.5

# 2. Install dependencies
uv sync --no-install-project
```

This creates a `.venv/` directory with all packages installed. You only need to do this once.

## Daily Usage

```bash
# Activate environment (for interactive shell sessions)
source .venv/bin/activate

# Or run commands directly without activating
uv run python src/some_script.py
uv run datasette -p 8001 mediameta.db
```

**Note:** `source .venv/bin/activate` requires the `.venv` to exist (see First Time Setup above). `uv run` also requires it but will error clearly if missing.

## Managing Dependencies

```bash
# Add a package
uv add package-name

# Add a specific version
uv add "package-name==1.2.3"

# Remove a package
uv remove package-name

# Update all packages
uv lock --upgrade
uv sync --no-install-project

# Update one package
uv lock --upgrade-package package-name
uv sync --no-install-project
```

## Environment Management

```bash
# Recreate environment from scratch
rm -rf .venv
uv venv --python 3.12.5
uv sync --no-install-project

# Install from existing lock file (e.g., after git pull)
uv sync --no-install-project
```

## Key Differences from pipenv

| pipenv | uv |
|--------|-----|
| `pipenv shell` | `source .venv/bin/activate` |
| `pipenv install pkg` | `uv add pkg` |
| `pipenv install` | `uv sync --no-install-project` |
| `pipenv run cmd` | `uv run cmd` |
| `pipenv --rm` | `rm -rf .venv` |
| `Pipfile` | `pyproject.toml` |
| `Pipfile.lock` | `uv.lock` |

## Why `--no-install-project`?

This flag is needed because the project isn't a distributable Python package (no `__init__.py` in `src/`). It tells uv to install only the dependencies listed in `pyproject.toml` without trying to install the project itself.

## Further Reading

- [uv documentation](https://docs.astral.sh/uv/)
- [pyproject.toml reference (PEP 621)](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
