# Mac Studio & Photo Processing Pipeline Planning

Discussion from 2026-02-16 exploring hardware upgrades, model choices, and a future photo curation pipeline.

## Current Setup

- **Machine**: MacBook Pro M3 Pro, 18GB RAM
- **Vision model**: SmolVLM2-2.2B via MLX (`mlx-community/SmolVLM2-2.2B-Instruct-mlx`)
- **Embedding model**: `sentence-transformers/all-MiniLM-L6-v2` (22M params, 256 max tokens, 384-dim)
- **CLIP model on disk**: `sentence-transformers/clip-ViT-B-32` (88M params, 512-dim)
- **Image thumbnails**: 31,841 files in `database/512x512/`

## Current Batch Job Performance

- **Rate**: ~1,132 images/hour (3.18s/image average)
- **Descriptions**: Concise 1-2 sentence outputs (e.g., "Two women are sitting at a table with a cake and wine.")
- **Prompt**: "briefly describe in one or two sentences"
- **Bottleneck**: Memory bandwidth (MLX inference is bandwidth-bound)

## Mac Studio M4 Max Consideration

**Specs**: M4 Max, 16-core CPU, 40-core GPU, 64GB RAM, 1TB — $2,899

| Spec | M3 Pro (current) | M4 Max (Mac Studio) |
|---|---|---|
| GPU cores | 18 | 40 |
| Memory | 18 GB | 64 GB |
| Memory bandwidth | ~150 GB/s | ~546 GB/s |

### Expected speedup for SmolVLM2 inference

- ~3.6x memory bandwidth advantage
- **Estimated rate**: ~3,500-4,000 images/hour (~0.9s/image)
- **Realistic speedup**: ~3x (accounting for non-GPU overhead)

### Key benefits for ongoing work

- **Larger models become practical**: 64GB allows 7B-13B+ vision models (bf16), 72B models (4-bit quantized ~40GB)
- **Always-on pipeline**: Desktop is ideal for persistent polling service, low power (~50W idle)
- **Frees laptop**: MacBook stays available for other work
- **Concurrent models**: Run vision model + CLIP + embedding model simultaneously

### Note on M4 Ultra

If models larger than ~30B or fine-tuning are needed, M4 Ultra (128GB, ~800 GB/s) is the step up. For 2B-13B range, M4 Max 64GB is the sweet spot.

## Planned Photo Curation Pipeline

Goal: Poll for new photos, process them, and help curate the library (a few photos/day ongoing).

### Pipeline stages

1. **Image descriptions** (current) — SmolVLM2 or larger vision model for text descriptions
2. **Duplicate/near-duplicate detection** — Timestamp clustering + CLIP image embeddings for visual similarity
3. **Quality filtering** — Blur detection (Laplacian variance), exposure analysis (histogram) — classical CV, no ML needed
4. **Low-content filtering** — Vision model scoring ("rate quality/interest 1-5") for accidental shots, blurry photos, etc.
5. **Best-shot selection** — From duplicate groups, pick best based on sharpness, exposure, composition, vision model rating

### Duplicate detection approach

- Cluster by timestamp (shots within a few seconds)
- Compute CLIP image embeddings for visual similarity
- Flag groups with timestamp < N seconds AND cosine similarity > 0.95
- Present in review UI for user to pick best shots

### UI approach

Review UI where suggestions are presented for approval/reject (not auto-hide). Tag-and-review method may be faster for some workflows.

## Embedding Model Considerations

### Current: all-MiniLM-L6-v2

- 22M params, 256 max tokens, 384-dim embeddings
- Fast, lightweight
- 256 token limit is NOT a constraint since descriptions are ~15-20 tokens

### Considered: e5-mistral-7b-instruct

- 7B params, 4096 max tokens, 4096-dim embeddings
- Significantly better semantic understanding
- ~14GB in bf16 — tight on M3 Pro, comfortable on Mac Studio 64GB
- Better for nuanced distinctions but may be overkill for 1-sentence descriptions
- Recommendation: Test on a sample before committing to see if retrieval quality actually improves

## CLIP Model Options for Image Embeddings

CLIP creates embeddings directly from image pixels (no text description needed). Maps images and text into the same vector space, enabling:
- **Image-to-image** similarity (find near-duplicates)
- **Text-to-image** search (search photos by typing a description)

### Models ranked

| Model | Size | Embedding dim | ImageNet accuracy | Open source | Notes |
|---|---|---|---|---|---|
| SigLIP 2 (Google, Feb 2025) | 400M-1B | 768-1152 | 85.0% | Yes (Apache 2.0) | Best overall, newest |
| DFN ViT-H (OpenCLIP) | ~1B | 1024 | 84.4% | Yes (MIT) | Very strong |
| SigLIP (Google) | ~400M | 768 | 82.0% | Yes (Apache 2.0) | Good balance |
| CLIP ViT-L/14 (OpenAI) | 428M | 768 | 75.5% | Yes (MIT) | Solid, well-supported |
| CLIP ViT-B/32 (on disk) | 88M | 512 | 63.2% | Yes (MIT) | Fast but weakest |

### Recommendation

- **SigLIP** via [OpenCLIP](https://github.com/mlfoundations/open_clip) — drop-in CLIP replacement with better visual understanding
- For near-duplicate detection (burst shots), even ViT-B/32 works fine
- Better models matter more for semantic similarity across different scenes

### CLIP performance estimates (31K images)

| Machine | Speed | Time for 31K images |
|---|---|---|
| M3 Pro | ~50-100 img/sec | ~5-10 minutes |
| M4 Max | ~150-300 img/sec | ~2-3 minutes |

CLIP is a single forward pass (not autoregressive), so it's orders of magnitude faster than generative vision models.

### Pairwise comparison

31K × 31K similarity matrix (~1 billion pairs) is just matrix math — takes seconds with numpy. Can also limit to within timestamp windows.

## Useful References

- [OpenCLIP](https://github.com/mlfoundations/open_clip) — open source CLIP implementation with SigLIP support
- [SigLIP 2 paper](https://arxiv.org/pdf/2502.14786) — latest multilingual vision-language encoders
- [mlx_clip](https://github.com/harperreed/mlx_clip) — CLIP on Apple Silicon via MLX
- [photo-similarity-search](https://github.com/harperreed/photo-similarity-search) — MLX-based CLIP photo similarity app (good reference for pipeline)
- [e5-mistral-7b-instruct](https://huggingface.co/intfloat/e5-mistral-7b-instruct) — larger embedding model
