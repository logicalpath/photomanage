# uv Usage Guide

Quick reference for using uv in this project.

## First Time Setup

After cloning the repo, create the virtual environment and install dependencies:

```bash
# 1. Create the virtual environment
uv venv --python 3.12.5

# 2. Install dependencies
uv sync
```

This creates a `.venv/` directory with all packages installed. You only need to do this once.

## Daily Usage

```bash
# Run commands with uv run (preferred)
uv run python src/some_script.py
uv run datasette -p 8001 mediameta.db
```

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
uv sync

# Update one package
uv lock --upgrade-package package-name
uv sync
```

## Environment Management

```bash
# Recreate environment from scratch
rm -rf .venv
uv venv --python 3.12.5
uv sync

# Install from existing lock file (e.g., after git pull)
uv sync
```

## Key Differences from pipenv

| pipenv | uv |
|--------|-----|
| `pipenv install pkg` | `uv add pkg` |
| `pipenv install` | `uv sync` |
| `pipenv run cmd` | `uv run cmd` |
| `pipenv --rm` | `rm -rf .venv` |
| `Pipfile` | `pyproject.toml` |
| `Pipfile.lock` | `uv.lock` |

## Further Reading

- [uv documentation](https://docs.astral.sh/uv/)
- [pyproject.toml reference (PEP 621)](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
