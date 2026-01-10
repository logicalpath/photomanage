# MLX-VLM and SmolVLM Usage Guide

This document provides comprehensive documentation for using mlx-vlm and SmolVLM in the photomanage project for AI-powered image description and analysis.

## Overview

mlx-vlm is actively used in this project for image description and vision-language model (VLM) tasks. It's a key component for AI-powered image analysis capabilities optimized for Apple Silicon Macs using the MLX framework.

**Inspiration:** This implementation was inspired by [Simon Willison's blog post on SmolVLM](https://simonwillison.net/2024/Nov/28/smolvlm/), which demonstrates practical applications of the SmolVLM model for image description tasks.

## Table of Contents

- [Dependencies and Installation](#dependencies-and-installation)
- [Model Cache](#model-cache)
- [SmolVLM Model Details](#smolvlm-model-details)
  - [How SmolVLM Creates Image Descriptions](#how-smolvlm-creates-image-descriptions)
- [Implementations](#implementations)
- [Usage Examples](#usage-examples)
- [Command-Line Interface](#command-line-interface)
- [Batch Processing](#batch-processing)
- [Output Formats](#output-formats)
- [Configuration Parameters](#configuration-parameters)
- [Database Integration](#database-integration)
- [External Resources](#external-resources)

## Dependencies and Installation

### Package Configuration

The project uses Pipenv for dependency management. mlx-vlm is explicitly listed in `Pipfile`:

```toml
[packages]
mlx-vlm = "*"
```

### Related Dependencies

- `mlx.core` - MLX framework for Apple Silicon
- `torch` and `torchvision` - PyTorch dependencies
- Python 3.x via `/opt/homebrew/bin/python3`

### Installation

Dependencies are managed via uv:

```bash
uv sync --no-install-project
```

You can also use `uv run` for running scripts with dependencies:

```bash
uv run --with mlx-vlm --with torch python -m mlx_vlm.generate [options]
```

**Note:** The `uv run` approach in `mlx/mlx-vlm.cli` was inspired by techniques from [Simon Willison's SmolVLM blog post](https://simonwillison.net/2024/Nov/28/smolvlm/).

## Model Cache

### Hugging Face Cache Location

When you first use SmolVLM, the model is automatically downloaded and cached locally by Hugging Face. The cache is stored at:

```
~/.cache/huggingface/hub/models--mlx-community--SmolVLM-Instruct-bf16/
```

### Benefits of Local Caching

- **No repeated downloads:** Once cached, the model loads instantly from disk
- **Offline usage:** Models can be used without internet connectivity
- **Faster startup:** Significantly reduces model loading time
- **Bandwidth savings:** ~500MB download only happens once

### Verifying Cached Models

To check if the model is already cached:

```bash
ls -la ~/.cache/huggingface/hub/ | grep SmolVLM
```

You should see a directory like:
```
models--mlx-community--SmolVLM-Instruct-bf16
```

### How Models are Loaded

When you specify `mlx-community/SmolVLM-Instruct-bf16` in any script, mlx-vlm automatically:
1. Checks the local cache first
2. Downloads the model only if not cached
3. Loads from cache for all subsequent uses

No additional configuration is needed - the caching is handled transparently.

### Managing the Cache

**View cache size:**
```bash
du -sh ~/.cache/huggingface/hub/models--mlx-community--SmolVLM-Instruct-bf16/
```

**Clear cache (if needed):**
```bash
rm -rf ~/.cache/huggingface/hub/models--mlx-community--SmolVLM-Instruct-bf16/
```

Note: The model will be re-downloaded on next use if you clear the cache.

## SmolVLM Model Details

This project supports both SmolVLM (original) and SmolVLM2 (next generation) models.

### SmolVLM vs SmolVLM2 Comparison

| Feature | SmolVLM (Original) | SmolVLM2 (NEW) |
|---------|-------------------|----------------|
| **Parameters** | 256M | 2.2B |
| **Model Size** | ~500MB | ~5.2GB |
| **Video Support** | ❌ No | ✅ Yes |
| **Math Problems (MathVista)** | 43.9 | 51.5 (+17%) |
| **OCR (OCRBench)** | 65.5 | 72.9 (+11%) |
| **Text Recognition (TextVQA)** | 72.1 | 73.21 |
| **Speed** | ⚡ Faster | 🎯 More capable |
| **Best For** | Quick descriptions, bulk processing | Complex tasks, OCR, video, math |
| **MLX Model Path** | `mlx-community/SmolVLM-Instruct-bf16` | `mlx-community/SmolVLM2-2.2B-Instruct-mlx` |

### SmolVLM (Original) - Primary Model

**Model:** `mlx-community/SmolVLM-Instruct-bf16`

- **Type:** Instruction-tuned vision-language model
- **Architecture:** SmolVLM (small VLM optimized for Apple Silicon)
- **Precision:** BF16 (brain float 16)
- **Parameters:** ~256M (small, efficient model)
- **Optimization:** Optimized for MLX framework on Apple Silicon

**Best for:** Fast image descriptions, bulk batch processing where speed matters

For detailed information about SmolVLM's architecture and capabilities, see the [Hugging Face SmolVLM blog post](https://huggingface.co/blog/smolvlm).

### SmolVLM2 (Next Generation) - NEW

**Model:** `mlx-community/SmolVLM2-2.2B-Instruct-mlx`

- **Type:** Advanced multimodal model (images, videos, and text)
- **Architecture:** SigLIP image encoder + SmolLM2-1.7B-Instruct
- **Precision:** BF16 (brain float 16)
- **Parameters:** 2.2B
- **Training Data:** 3.3M samples (34% images, 33% video, 20% text, 12% multi-image)
- **GPU RAM Required:** ~5.2GB for video inference

**NEW Capabilities:**
- **Video understanding** - Natively processes video files (requires `decord` library)
- **Improved math reasoning** - Better at solving math problems in images
- **Enhanced OCR** - Superior text extraction from photos and documents
- **Complex diagrams** - Better understanding of scientific diagrams and charts
- **Multi-image comparison** - Can analyze multiple images together

**Best for:** OCR tasks, math problems, video analysis, complex visual reasoning

**Model Page:** [HuggingFaceTB/SmolVLM2-2.2B-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct)

**Blog Post:** [SmolVLM2: Bringing Video Understanding to Every Device](https://huggingface.co/blog/smolvlm2)

### How SmolVLM Creates Image Descriptions

SmolVLM is a **Vision Language Model (VLM)** that can understand both images and text. Here's how it works to create descriptions:

#### 1. **Model Components**

The model consists of three main parts:
- **Vision Encoder**: Processes the image and extracts visual features
- **Language Model**: Generates natural language text
- **Projection Layer**: Connects vision features to the language model

#### 2. **The Description Process**

When you ask SmolVLM to describe an image, here's what happens:

**Step 1: Load the Model**
```python
model, processor = load("mlx-community/SmolVLM-Instruct-bf16")
config = load_config("mlx-community/SmolVLM-Instruct-bf16")
```
- The model is loaded from cache (~/.cache/huggingface/hub/)
- The processor handles image preprocessing and tokenization
- The config contains model-specific settings

**Step 2: Prepare the Prompt**
```python
prompt = "Describe this image in detail."
formatted_prompt = apply_chat_template(processor, config, prompt, temp=0.0, max_tokens=100)
```
- Your text prompt is formatted using a chat template
- Generation parameters (temperature, max_tokens) are applied
- The template structures the prompt for the instruction-tuned model

**Step 3: Image Processing**
```python
image_paths = ["/path/to/image.jpg"]
```
- The image is loaded and preprocessed by the processor
- It's resized and normalized to match the model's training
- Visual features are extracted by the vision encoder

**Step 4: Generation**
```python
output = generate(model, processor, formatted_prompt, image_paths, verbose=False)
```
- The vision encoder processes the image into feature vectors
- These features are projected into the language model's space
- The language model generates text tokens autoregressively (one token at a time)
- Each new token is influenced by both the image features and previous tokens
- Generation continues until max_tokens is reached or a stop token is generated

**Step 5: Output**
```python
print(output)  # "A person standing on a beach with the ocean in the background."
```
- The tokens are decoded back into human-readable text
- You receive a natural language description of what's in the image

#### 3. **Key Parameters Affecting Output**

- **Temperature (temp)**: Controls randomness
  - `0.0` = Always picks the most likely next token (deterministic)
  - `0.5+` = More creative, varied descriptions

- **Max Tokens**: Limits description length
  - `100` = Brief description (~1-2 sentences)
  - `500` = Detailed, comprehensive description

- **Prompt**: Guides what the model focuses on
  - `"Describe this image in detail"` = General description
  - `"What objects can you see?"` = Focus on objects
  - `"What is the mood of this image?"` = Focus on atmosphere

#### 4. **Why It Works Well on Apple Silicon**

- **MLX Framework**: Built specifically for Apple Silicon (M1/M2/M3)
- **BF16 Precision**: Brain Float 16 is efficient on Apple's Neural Engine
- **Small Model Size**: 256M parameters fit entirely in unified memory
- **On-Device Processing**: No internet required, no cloud costs

### Alternative Models

The codebase also references:
- `mlx-community/Qwen2-VL-2B-Instruct-4bit` (found in `src/SmolVLMExampleAlpa.py`)

## Implementations

The project contains several implementations for both SmolVLM and SmolVLM2:

### 1. SmolVLMHelper Class (Original Model)

**File:** `src/smolvlm-helper.py`

A high-level wrapper class for image description tasks using the original SmolVLM model.

**Key Features:**
- Single and batch image processing
- Customizable parameters (temperature, max_tokens, prompt)
- Built-in error handling
- Directory processing with file type filtering

**Methods:**

#### `describe_image()`
Analyze a single image or multiple images.

**Parameters:**
- `image_path` (str or list): Path(s) to image file(s)
- `prompt` (str): Analysis prompt (default: "Describe this image in detail")
- `temp` (float): Temperature for generation (0.0 = deterministic, higher = more random)
- `max_tokens` (int): Maximum output length

**Returns:** Description string or dictionary of results

#### `batch_describe_images()`
Process entire directories of images.

**Parameters:**
- `directory` (str): Path to directory containing images
- `file_types` (list): File extensions to process (default: ['.jpg', '.jpeg', '.png', '.arw', '.nef'])
- `max_images` (int, optional): Maximum number of images to process
- `prompt` (str): Analysis prompt
- `temp` (float): Temperature
- `max_tokens` (int): Maximum output length

**Returns:** Dict[filename → description]

### 2. SmolVLM2Helper Class (Next Generation Model) - NEW

**File:** `src/smolvlm2-helper.py`

A high-level wrapper class for SmolVLM2 with enhanced capabilities including video support.

**Key Features:**
- Image and video processing (video is NEW!)
- Enhanced math reasoning and OCR capabilities
- Multi-image comparison support
- Same API as SmolVLMHelper for easy migration
- Built-in error handling

**Methods:**

#### `describe_image()`
Analyze images with enhanced capabilities (better OCR, math, diagrams).

**Parameters:**
- `image_path` (str or list): Path(s) to image file(s)
- `prompt` (str): Analysis prompt (default: "Describe this image in detail")
- `temp` (float): Temperature for generation
- `max_tokens` (int): Maximum output length

**Returns:** Description string or dictionary of results

#### `describe_video()` - NEW!
Analyze video content.

**Parameters:**
- `video_path` (str): Path to video file
- `prompt` (str): Analysis prompt (default: "Describe what happens in this video")
- `temp` (float): Temperature for generation
- `max_tokens` (int): Maximum output length (videos typically need more tokens)

**Returns:** Video description string

**Note:** Requires `decord` library: `pip install decord`

#### `batch_describe_images()`
Process entire directories of images.

**Parameters:** Same as SmolVLMHelper.batch_describe_images()

**Returns:** Dict[filename → description]

#### `batch_describe_videos()` - NEW!
Process entire directories of videos.

**Parameters:**
- `directory` (str): Path to directory containing videos
- `file_types` (list): Video file extensions (default: ['.mp4', '.mov', '.avi', '.mkv'])
- `max_videos` (int, optional): Maximum number of videos to process
- `prompt` (str): Analysis prompt
- `temp` (float): Temperature
- `max_tokens` (int): Maximum output length

**Returns:** Dict[filename → description]

### 3. Direct Implementation Examples

#### `src/run_mlx_vlm.py`
Simple example showing direct mlx-vlm API usage:
- Model loading: `load(model_path)`
- Config loading: `load_config(model_path)`
- Prompt formatting: `apply_chat_template()`
- Generation: `generate()`

#### `src/SmolVLM.py`
Alternative direct implementation with database image examples.

#### `src/SmolVLMExampleAlpa.py`
Advanced implementation featuring:
- `ModelComponents` dataclass for organized model storage
- `loadModel()` function for reusable initialization
- Per-image error handling in batch processing

### 3. Subprocess-Based Scripts

#### `src/image_description.py`
Simple wrapper that:
- Calls `uv run` with mlx-vlm dependencies
- Runs `python -m mlx_vlm.generate` as subprocess
- Captures stdout/stderr
- Saves analysis to timestamped text file in `outputs/` directory

**Usage:**
```bash
python src/image_description.py /path/to/image.jpg
```

#### `src/image_description2.py`
Click CLI application for batch processing:
- Processes multiple images (specified via command-line count)
- Supported formats: .jpg, .jpeg, .nef, .arw
- Runs `uv run` subprocess for each image
- Extracts clean response text
- Outputs JSON file with relative paths and descriptions

#### `src/image_description3.py`
Similar to image_description2.py, but also:
- Writes all processed image paths to `list_thumbs.txt`
- Same JSON output format with timestamp

## Usage Examples

### Using SmolVLMHelper

**Single Image Analysis:**

```python
from smolvlm_helper import SmolVLMHelper

vlm = SmolVLMHelper()
result = vlm.describe_image("/path/to/image.jpg")
print(result)
```

**Multiple Images:**

```python
vlm = SmolVLMHelper()
results = vlm.describe_image([
    "/path/to/image1.jpg",
    "/path/to/image2.jpg"
])
```

**Batch Processing Directory:**

```python
vlm = SmolVLMHelper()
results = vlm.batch_describe_images(
    directory="/path/to/images",
    max_images=10,
    file_types=['.jpg', '.jpeg', '.png']
)

for filename, description in results.items():
    print(f"{filename}: {description}")
```

**Custom Parameters:**

```python
vlm = SmolVLMHelper()
result = vlm.describe_image(
    image_path="/path/to/image.jpg",
    prompt="What objects can you see in this image?",
    temp=0.2,
    max_tokens=200
)
```

### Using SmolVLM2Helper - NEW

**Single Image Analysis:**

```python
from smolvlm2_helper import SmolVLM2Helper

vlm2 = SmolVLM2Helper()
result = vlm2.describe_image("/path/to/image.jpg")
print(result)
```

**Single Video Analysis (NEW!):**

```python
from smolvlm2_helper import SmolVLM2Helper

# Note: Requires 'pip install decord' for video support
vlm2 = SmolVLM2Helper()
result = vlm2.describe_video("/path/to/video.mp4")
print(result)
```

**OCR / Text Extraction (Improved in SmolVLM2):**

```python
vlm2 = SmolVLM2Helper()
result = vlm2.describe_image(
    image_path="document.jpg",
    prompt="Extract all text from this image.",
    max_tokens=500
)
print(result)
```

**Math Problem Solving (Improved in SmolVLM2):**

```python
vlm2 = SmolVLM2Helper()
result = vlm2.describe_image(
    image_path="math_problem.jpg",
    prompt="Solve the math problem in this image and explain your steps.",
    max_tokens=300
)
print(result)
```

**Batch Image Processing:**

```python
vlm2 = SmolVLM2Helper()
results = vlm2.batch_describe_images(
    directory="/path/to/images",
    max_images=10
)

for filename, description in results.items():
    print(f"{filename}: {description}")
```

**Batch Video Processing (NEW!):**

```python
vlm2 = SmolVLM2Helper()
results = vlm2.batch_describe_videos(
    directory="/path/to/videos",
    max_videos=5,
    max_tokens=300
)

for filename, description in results.items():
    print(f"{filename}: {description}")
```

### Direct API Usage

```python
import mlx.core as mx
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

model_path = "mlx-community/SmolVLM-Instruct-bf16"

# Load model and config
model, processor = load(model_path)
config = load_config(model_path)

# Prepare prompt
prompt = "Describe this image in detail"
formatted_prompt = apply_chat_template(
    processor,
    config,
    prompt,
    temp=0.0,
    max_tokens=500
)

# Generate description
output = generate(
    model,
    processor,
    formatted_prompt,
    ["/path/to/image.jpg"],
    verbose=False
)

print(output)
```

## Command-Line Interface

### Direct Command

```bash
python -m mlx_vlm.generate \
  --model mlx-community/SmolVLM-Instruct-bf16 \
  --max-tokens 500 \
  --temp 0.0 \
  --prompt "Describe this image in detail" \
  --image /path/to/image.jpg
```

### Using uv Package Runner

**SmolVLM (Original):**
```bash
uv run --with mlx-vlm --with torch python -m mlx_vlm.generate \
  --model mlx-community/SmolVLM-Instruct-bf16 \
  --max-tokens 500 \
  --temp 0.5 \
  --prompt "Describe this image in detail" \
  --image test.jpg
```

**SmolVLM2 (Next Generation):**

Image description:
```bash
uv run --with mlx-vlm --with torch python -m mlx_vlm.generate \
  --model mlx-community/SmolVLM2-2.2B-Instruct-mlx \
  --max-tokens 500 \
  --temp 0.0 \
  --prompt "Describe this image in detail" \
  --image photo.jpg
```

OCR / Text extraction (SmolVLM2 excels at this):
```bash
uv run --with mlx-vlm --with torch python -m mlx_vlm.generate \
  --model mlx-community/SmolVLM2-2.2B-Instruct-mlx \
  --max-tokens 500 \
  --temp 0.0 \
  --prompt "Extract all text from this image" \
  --image document.jpg
```

Math problem solving (SmolVLM2 improved):
```bash
uv run --with mlx-vlm --with torch python -m mlx_vlm.generate \
  --model mlx-community/SmolVLM2-2.2B-Instruct-mlx \
  --max-tokens 500 \
  --temp 0.0 \
  --prompt "Solve the math problem in this image and explain your steps" \
  --image math_problem.jpg
```

Video description (NEW in SmolVLM2 - requires `pip install decord`):
```bash
uv run --with mlx-vlm --with torch --with decord python -m mlx_vlm.generate \
  --model mlx-community/SmolVLM2-2.2B-Instruct-mlx \
  --max-tokens 500 \
  --temp 0.0 \
  --prompt "Describe what happens in this video" \
  --image video.mp4
```

**CLI Reference:** See `mlx/mlx-vlm.cli` for detailed command-line examples.

## Batch Processing

### Supported Image Formats

All implementations support the following formats:
- `.jpg` / `.jpeg` - JPEG images
- `.png` - PNG images
- `.arw` - Sony RAW format
- `.nef` - Nikon RAW format

### Batch Processing Scripts

The project includes three batch processing scripts that generate timestamped JSON output files:

**Output Directory:** `outputs/`

**Example Output Files:**
- `image_analysis_20250202_163500.json`
- `image_analysis_20250202_165436.json`
- `image_analysis_20250209_113513.json`

### JSON Output Structure

```json
{
  "file": "relative/path/to/image.jpg",
  "description": "AI-generated description text"
}
```

## Output Formats

### JSON Files
Batch processing scripts output to timestamped JSON files in `outputs/`:
- Relative file paths
- Generated descriptions
- Timestamp in filename for versioning

### Text Files
Simple text file output for single image analysis.

### Console Output
Direct printing of descriptions for interactive use.

## Configuration Parameters

### Model Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--model` | str | `mlx-community/SmolVLM-Instruct-bf16` | Model identifier |
| `--max-tokens` | int | 100-500 | Maximum output length |
| `--temp` | float | 0.0-0.5 | Temperature for generation (0.0 = deterministic) |
| `--prompt` | str | "Describe this image in detail" | Analysis prompt |
| `--image` | str | Required | Path to image file |

### Temperature Guidelines

- **0.0**: Fully deterministic output (recommended for consistent descriptions)
- **0.2-0.3**: Slightly varied output while staying focused
- **0.5+**: More creative and varied descriptions

### Max Tokens Guidelines

- **100**: Brief, concise descriptions
- **200-300**: Standard detailed descriptions
- **500+**: Very detailed, comprehensive analysis

## Database Integration

### AI Description Table

The `ai_description` table in `database/mediameta.db` was created and populated using the code in this repository.

**Table Schema:**
```sql
CREATE TABLE ai_description (
   file TEXT,
   description TEXT
)
```

### Loading Descriptions into Database

The batch processing scripts (`image_description2.py`, `image_description3.py`) output JSON files in the format required by the database. To load these descriptions into the database:

**Using sqlite-utils:**
```bash
# Load a single JSON file
sqlite-utils insert database/mediameta.db ai_description \
  outputs/image_analysis_20250202_163500.json --json

# Or load multiple JSON files
for file in outputs/image_analysis_*.json; do
  sqlite-utils insert database/mediameta.db ai_description "$file" --json
done
```

**Note:** `sqlite-utils` is included in the project's Pipfile dependencies.

### Querying AI Descriptions

The database includes an index on `ai_description.file` for efficient JOINs:

```sql
CREATE INDEX idx_ai_description_file ON ai_description(file);
```

### Combining Thumbnails with Descriptions

This query from `database/datasette.yaml` combines thumbnail images with their AI-generated descriptions, allowing you to display images alongside their descriptions:

```sql
SELECT thumbImages.content, exif.CreateDate,
       thumbImages.path as thumbPath,
       ai_description.file as aiFile,
       ai_description.description
FROM ai_description
INNER JOIN thumbImages ON (
  ai_description.file = thumbImages.path OR
  replace(lower(ai_description.file), '.jpg', '.jpeg') = lower(thumbImages.path) OR
  lower(ai_description.file) = lower(thumbImages.path)
)
INNER JOIN exif ON thumbImages.path = exif.SourceFile
ORDER BY exif.CreateDate ASC;
```

**What this query returns:**
- `thumbImages.content` - The actual thumbnail image data (can be displayed in Datasette)
- `exif.CreateDate` - When the photo was taken
- `thumbImages.path` - Path to the thumbnail
- `ai_description.file` - Path from the AI description record
- `ai_description.description` - The AI-generated description text

**Use case:** This query is particularly useful for browsing your photo collection chronologically while seeing both the visual thumbnail and the AI-generated description of what's in each image.

## Current Use Cases

Based on codebase analysis, mlx-vlm is used for:

1. **Photo Cataloging:** Generating AI descriptions for photo collections
2. **Image Analysis:** Detailed visual understanding of image content
3. **Database Enhancement:** Enriching media metadata with AI-generated descriptions (see `ai_description` table)
4. **Batch Processing:** Processing entire image directories programmatically
5. **Local Processing:** On-device processing (Apple Silicon) without cloud dependencies

## Performance Considerations

### Apple Silicon Optimization

SmolVLM is specifically optimized for Apple Silicon through the MLX framework:
- Efficient BF16 precision
- Small model size (~256M parameters)
- Fast inference on M1/M2/M3 chips
- No GPU/cloud dependencies

### Batch Processing Tips

1. Use `SmolVLMHelper.batch_describe_images()` for large batches
2. Set `max_images` parameter to limit processing
3. Consider temperature=0.0 for consistent results
4. Monitor memory usage for very large batches

## Additional Resources

### Project Files

- **Helper Notes:** `notes/use_vlm_helper.txt`
- **CLI Documentation:** `mlx/mlx-vlm.cli`
- **Example Outputs:** `outputs/image_analysis_*.json`

## External Resources

### Blog Posts and Documentation

- **[Simon Willison: SmolVLM - a 2 billion parameter vision LLM you can run on a Mac](https://simonwillison.net/2024/Nov/28/smolvlm/)** - Practical guide and inspiration for this implementation, including the `uv run` approach used in `mlx/mlx-vlm.cli`

- **[Hugging Face: SmolVLM - Small yet Mighty Vision Language Model](https://huggingface.co/blog/smolvlm)** - Official blog post explaining SmolVLM architecture, capabilities, and usage

- **[Hugging Face: SmolVLM2 - Bringing Video Understanding to Every Device](https://huggingface.co/blog/smolvlm2)** - NEW! Official blog post about SmolVLM2 with video support and improved capabilities

### Model Pages

**SmolVLM (Original):**
- **[mlx-community/SmolVLM-Instruct-bf16](https://huggingface.co/mlx-community/SmolVLM-Instruct-bf16)** - MLX-optimized model (256M parameters)

**SmolVLM2 (Next Generation):**
- **[mlx-community/SmolVLM2-2.2B-Instruct-mlx](https://huggingface.co/mlx-community/SmolVLM2-2.2B-Instruct-mlx)** - MLX-optimized SmolVLM2 (2.2B parameters)
- **[HuggingFaceTB/SmolVLM2-2.2B-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct)** - Original PyTorch model with full documentation

### Related Tools

- **[MLX Framework](https://github.com/ml-explore/mlx)** - Apple's machine learning framework for Apple Silicon
- **[mlx-vlm](https://github.com/Blaizzy/mlx-vlm)** - Vision Language Models for MLX
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package installer and runner

## Summary

| Aspect | Details |
|--------|---------|
| **Status** | Actively used in production |
| **Package Manager** | Pipenv |
| **Framework** | MLX (Apple Silicon optimized) |
| **Primary Model** | SmolVLM-Instruct-bf16 |
| **Recommended API** | `SmolVLMHelper` class |
| **Image Formats** | JPG, JPEG, NEF, ARW, PNG |
| **Output Formats** | JSON, TXT, Console |
| **Use Cases** | Photo cataloging, image analysis, metadata enhancement |
| **Execution Methods** | Direct API, CLI, subprocess wrappers |

---

**Last Updated:** 2025-11-21
