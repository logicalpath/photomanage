# Claude Code Rules

## Git Workflow

- **NEVER make changes directly on `main`.** Always create a feature or fix branch before editing any files.

## Security

- **Never store secrets in files.** Passwords, hashes, tokens, and API keys must be stored in environment variables, not in `datasette.yaml`, `.env`, or any other committed file. Use datasette's `$env` syntax: `my_key:\n  $env: MY_ENV_VAR`
