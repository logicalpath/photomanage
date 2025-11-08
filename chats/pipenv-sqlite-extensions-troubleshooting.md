# Fixing Python SQLite Extensions with Pyenv and Pipenv

## Problem Summary
Datasette was unable to load the spatialite extension due to Python not being compiled with SQLite extension support.

## Initial Issue

```bash
datasette -p 8001 --root --load-extension=spatialite -c datasette.yaml mediameta.db
# Error: Your Python installation does not have the ability to load SQLite extensions.
```

## Troubleshooting Steps

### 1. Pipenv Python Path Mismatch

**Problem:** Pipenv was looking for Python at `/opt/homebrew/bin/python3` but system was using pyenv.

```bash
which python
# /Users/eddiedickey/.pyenv/shims/python

pipenv shell
# Warning: Python /opt/homebrew/bin/python3 was not found on your system...
```

**Solution:** Set the `PIPENV_PYTHON` environment variable

```bash
export PIPENV_PYTHON="$HOME/.pyenv/shims/python"

# Make it permanent by adding to shell config
echo 'export PIPENV_PYTHON="$HOME/.pyenv/shims/python"' >> ~/.zshrc
```

### 2. SQLite Extensions Not Loading

**Problem:** Python wasn't compiled with SQLite extension support.

**Testing for the issue:**

```bash
python -c "import sqlite3; print(sqlite3.connect(':memory:').enable_load_extension(True))"
# AttributeError: 'sqlite3.Connection' object has no attribute 'enable_load_extension'
```

**Check current Python compilation flags:**

```bash
python -c "import sysconfig; print(sysconfig.get_config_var('CONFIG_ARGS'))"
# Missing: --enable-loadable-sqlite-extensions
```

### 3. First Reinstall Attempt (Incomplete)

```bash
PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions" pyenv install 3.12.5 --force
```

This added the flag but Python was still using the macOS system SQLite instead of homebrew's SQLite.

**Verification showed:**

```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
# 3.43.2  (macOS system SQLite)

brew list sqlite
# Shows SQLite 3.50.4 installed via homebrew
```

### 4. Final Solution

**Force Python to use homebrew's SQLite with proper compilation flags:**

```bash
PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions" \
LDFLAGS="-L/opt/homebrew/opt/sqlite/lib" \
CPPFLAGS="-I/opt/homebrew/opt/sqlite/include" \
pyenv install 3.12.5 --force
```

**Verify the fix:**

```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
# 3.50.4  ✓

python -c "import sqlite3; print(sqlite3.connect(':memory:').enable_load_extension(True))"
# None  ✓ (success)
```

### 5. Recreate Pipenv Environment

```bash
pipenv --rm
pipenv install
pipenv shell

# Now datasette works with spatialite
datasette -p 8001 --root --load-extension=spatialite -c datasette.yaml mediameta.db
```

## Key Takeaways

1. **PIPENV_PYTHON environment variable** ensures Pipenv uses the correct Python installation
2. **--enable-loadable-sqlite-extensions** flag is required when compiling Python
3. **LDFLAGS and CPPFLAGS** must point to homebrew's SQLite, not macOS system SQLite
4. After recompiling Python, recreate virtual environments to use the updated Python

## Environment Details

- **OS:** macOS with Xcode SDK
- **Python:** 3.12.5 (pyenv)
- **SQLite:** 3.50.4 (homebrew)
- **Tool:** Pipenv for virtual environment management
- **Extension:** spatialite for geographic data
