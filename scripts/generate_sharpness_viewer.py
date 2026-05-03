#!/usr/bin/env python3
"""
Generate a standalone HTML viewer for sharpness-scored thumbnails.

Reads sharpness_scores.json and produces an HTML file with a thumbnail grid
sorted by sharpness score (lowest first). Includes a range slider to filter
by score threshold.

Usage:
    python scripts/generate_sharpness_viewer.py
    python scripts/generate_sharpness_viewer.py --json-file outputs/v2/sharpness_scores.json
    python scripts/generate_sharpness_viewer.py --thumb-dir database/512x512 --output outputs/v2/sharpness_viewer.html
    python scripts/generate_sharpness_viewer.py --max-images 500
"""

import argparse
import json
from pathlib import Path


DEFAULT_JSON = "outputs/v2/sharpness_scores.json"
DEFAULT_THUMB_DIR = "database/512x512"
DEFAULT_OUTPUT = "outputs/v2/sharpness_viewer.html"
DEFAULT_MAX_IMAGES = 500


def file_path_to_thumb(file_entry: str, thumb_dir: str) -> str:
    """Convert ./0/filename.ext to a relative path from the output file location."""
    p = Path(file_entry)
    # outputs/v2/sharpness_viewer.html -> ../../database/512x512/0/filename.ext
    return f"../../{thumb_dir}/{p.parts[-2]}/{p.name}"


def main():
    parser = argparse.ArgumentParser(description="Generate HTML thumbnail viewer sorted by sharpness")
    parser.add_argument("--json-file", default=DEFAULT_JSON, help=f"Sharpness scores JSON (default: {DEFAULT_JSON})")
    parser.add_argument("--thumb-dir", default=DEFAULT_THUMB_DIR, help=f"Thumbnail root directory (default: {DEFAULT_THUMB_DIR})")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Output HTML file (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--max-images", type=int, default=DEFAULT_MAX_IMAGES, help=f"Maximum images to include (default: {DEFAULT_MAX_IMAGES})")
    args = parser.parse_args()

    with open(args.json_file) as f:
        scores = json.load(f)

    scores.sort(key=lambda x: x["sharpness"] or 0)
    subset = scores[:args.max_images]

    min_score = subset[0]["sharpness"]
    max_score = subset[-1]["sharpness"]

    cards = []
    for entry in subset:
        score = entry["sharpness"]
        thumb = file_path_to_thumb(entry["file"], args.thumb_dir)
        filename = Path(entry["file"]).name
        cards.append(f'''
        <div class="card" data-score="{score:.1f}">
            <img src="{thumb}" alt="{filename}" loading="lazy" onerror="this.parentElement.style.display='none'">
            <div class="label">
                <span class="score">{score:.1f}</span>
                <span class="filename">{filename}</span>
            </div>
        </div>''')

    cards_html = "\n".join(cards)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sharpness Viewer — Truncated Descriptions</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, sans-serif; background: #111; color: #eee; padding: 16px; }}
  header {{ margin-bottom: 16px; }}
  h1 {{ font-size: 1.2rem; font-weight: 600; margin-bottom: 8px; }}
  .controls {{ display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }}
  .controls label {{ font-size: 0.85rem; color: #aaa; }}
  .controls input[type=range] {{ width: 240px; }}
  #score-display {{ font-size: 0.85rem; color: #fff; min-width: 120px; }}
  #count {{ font-size: 0.85rem; color: #aaa; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 8px;
  }}
  .card {{
    background: #222;
    border-radius: 6px;
    overflow: hidden;
    cursor: default;
  }}
  .card img {{
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    display: block;
  }}
  .label {{
    padding: 6px 8px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}
  .score {{
    font-size: 0.9rem;
    font-weight: 700;
    color: #f90;
  }}
  .filename {{
    font-size: 0.65rem;
    color: #888;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .hidden {{ display: none !important; }}
</style>
</head>
<body>
<header>
  <h1>Sharpness Viewer &mdash; {len(subset):,} lowest-scoring truncated images</h1>
  <div class="controls">
    <label>Max sharpness: <input type="range" id="threshold" min="{min_score:.0f}" max="{max_score:.0f}" value="{max_score:.0f}" step="1"></label>
    <span id="score-display">&le; {max_score:.0f}</span>
    <span id="count">{len(subset):,} shown</span>
  </div>
</header>
<div class="grid" id="grid">
{cards_html}
</div>
<script>
  const slider = document.getElementById('threshold');
  const display = document.getElementById('score-display');
  const countEl = document.getElementById('count');
  const cards = document.querySelectorAll('.card');

  slider.addEventListener('input', () => {{
    const max = parseFloat(slider.value);
    display.textContent = '≤ ' + max.toFixed(0);
    let visible = 0;
    cards.forEach(card => {{
      const score = parseFloat(card.dataset.score);
      if (score <= max) {{ card.classList.remove('hidden'); visible++; }}
      else {{ card.classList.add('hidden'); }}
    }});
    countEl.textContent = visible.toLocaleString() + ' shown';
  }});
</script>
</body>
</html>"""

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        f.write(html)

    print(f"Written: {args.output}")
    print(f"Images:  {len(subset):,} (score range {min_score:.1f} – {max_score:.1f})")
    print(f"Open:    open {args.output}")


if __name__ == "__main__":
    main()
