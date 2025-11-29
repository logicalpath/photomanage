# Batch Processing Performance Analysis

Analysis date: 2025-11-25

## Overview

Performance data collected during batch image description generation using SmolVLM models.

## Dataset

- **Total files to process:** 31,841
- **Files analyzed:** 3,199 (successful entries)
- **NEF files in sample:** 571

Note: Files with `.NEF` extension are actually JPEG thumbnails - the original filename/extension was preserved during thumbnail creation.

## Processing Time Statistics

### All Files

| Metric | Value |
|--------|-------|
| Median | 10.02s |
| Mean | 25.15s |
| Std Dev | 99.90s |

### NEF Files Only

| Metric | Value |
|--------|-------|
| Median | 10.07s |
| Mean | 24.27s |
| Std Dev | 95.41s |
| Min | 5.31s |
| Max | 1028.15s (~17 min) |

## Key Findings

1. **NEF files process at the same rate as other files** - The `.NEF` extension doesn't impact processing time since these are actually JPEG files internally.

2. **Significant outliers exist** - Some files take 10-17+ minutes to process, while most complete in ~10 seconds.

3. **Mean vs Median discrepancy** - The mean (25s) is 2.5x higher than the median (10s) due to long-tail outliers.

4. **Time estimates are optimistic when using median:**
   - Median-based estimate: 10s × 31,841 = ~88 hours (~3.7 days)
   - Mean-based estimate: 25s × 31,841 = ~221 hours (~9.2 days)

## Outlier Impact

The high standard deviation (~100s) indicates extreme variability. Even a handful of 17-minute files per batch can add hours to total runtime. Outliers may be caused by:

- Images that confuse the model
- System resource contention
- Memory pressure during processing

## Models

Data collected primarily from `smolvlm` model. Comparison with `smolvlm2` pending additional data collection.

## Future Analysis

- Compare processing times between smolvlm and smolvlm2
- Identify characteristics of outlier images
- Analyze description quality differences between models
