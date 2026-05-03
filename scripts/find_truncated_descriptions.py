#!/usr/bin/env python3
"""
Find truncated descriptions from a v2 image analysis run.

Entries where generation_tokens equals the max_tokens cap (default: 80) were
cut off mid-sentence and need to be re-run.

Usage:
    python scripts/find_truncated_descriptions.py
    python scripts/find_truncated_descriptions.py --input outputs/v2/image_analysis.json --output outputs/v2/truncated_descriptions.yaml
    python scripts/find_truncated_descriptions.py --max-tokens 100
"""

import argparse
import json
from pathlib import Path

import yaml


DEFAULT_INPUT = "outputs/v2/image_analysis.json"
DEFAULT_OUTPUT = "outputs/v2/truncated_descriptions.yaml"
DEFAULT_MAX_TOKENS = 80


def main():
    parser = argparse.ArgumentParser(description="Find truncated image descriptions")
    parser.add_argument("--input", default=DEFAULT_INPUT, help=f"Input JSON file (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Output YAML file (default: {DEFAULT_OUTPUT})")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"Token cap used during generation — entries at this limit are truncated (default: {DEFAULT_MAX_TOKENS})",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    with open(input_path) as f:
        data = json.load(f)

    truncated = [entry for entry in data if entry.get("generation_tokens") == args.max_tokens]

    print(f"Total entries:     {len(data):,}")
    print(f"Truncated entries: {len(truncated):,} (generation_tokens == {args.max_tokens})")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(truncated, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"Written to:        {output_path}")


if __name__ == "__main__":
    main()
