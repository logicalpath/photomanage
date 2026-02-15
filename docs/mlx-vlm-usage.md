# MLX-VLM and SmolVLM2 Usage Guide

Generate AI-powered image descriptions using SmolVLM2 on Apple Silicon via the MLX framework. Descriptions are stored in the `image_description` table in `database/mediameta.db`.

## Installation

Dependencies are managed via uv with `pyproject.toml`:

```bash
uv sync
```

The first run will download the SmolVLM2 model (~5.2GB) to `~/.cache/huggingface/hub/`.

## Quick Start

### Describe a few images

```bash
uv run python src/generate_descriptions.py database/512x512 10
```

### Run a full batch

```bash
./scripts/run_batch_descriptions.sh
```

See [docs/batch-processing-guide.md](batch-processing-guide.md) for monitoring, stopping, resuming, and troubleshooting batch runs.

### Import descriptions into the database

```bash
python scripts/import_image_descriptions.py
```

## How It Works

1. `generate_descriptions.py` processes images using `SmolVLM2Helper` and writes results to `outputs/image_analysis.json`
2. `batch_orchestrator.py` runs `generate_descriptions.py` in subprocess batches for memory safety
3. `import_image_descriptions.py` loads the JSON into the `image_description` table

### Default Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max-tokens` | `100` | Maximum output tokens per image |
| `--prompt` | `Briefly describe this image in one or two sentences.` | Description prompt |
| `--temp` | `0.0` | Temperature (0.0 = deterministic) |

## Model

**SmolVLM2-2.2B-Instruct-mlx** (`mlx-community/SmolVLM2-2.2B-Instruct-mlx`)

- 2.2B parameters, ~5.2GB
- SigLIP image encoder + SmolLM2-1.7B-Instruct
- Supports images and video
- Optimized for Apple Silicon via MLX

## Python API

```python
from smolvlm2_helper import SmolVLM2Helper

vlm = SmolVLM2Helper()
result = vlm.describe_image("/path/to/image.jpg")
print(result)
```

## Key Files

| File | Purpose |
|------|---------|
| `src/generate_descriptions.py` | Per-batch image processor |
| `src/batch_orchestrator.py` | Orchestrates batches with memory management |
| `src/smolvlm2_helper.py` | SmolVLM2 Python wrapper |
| `scripts/run_batch_descriptions.sh` | Start batch processing |
| `scripts/stop_batch_descriptions.sh` | Stop batch processing |
| `scripts/import_image_descriptions.py` | Load JSON results into SQLite |

## External Resources

- [SmolVLM2 blog post](https://huggingface.co/blog/smolvlm2)
- [mlx-community/SmolVLM2-2.2B-Instruct-mlx](https://huggingface.co/mlx-community/SmolVLM2-2.2B-Instruct-mlx)
- [mlx-vlm](https://github.com/Blaizzy/mlx-vlm)
- [Simon Willison's SmolVLM post](https://simonwillison.net/2024/Nov/28/smolvlm/) (original inspiration)
