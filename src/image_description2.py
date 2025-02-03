# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
# ]
# ///

import click
import subprocess
import json
from datetime import datetime
import os
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.nef', '.arw'}

def is_image_file(path):
    """Check if a file is an image based on its extension."""
    return path.suffix.lower() in IMAGE_EXTENSIONS

def find_image_files(directory):
    """Recursively find all image files in a directory."""
    image_files = []
    directory_path = Path(directory).resolve()
    
    for path in directory_path.rglob('*'):
        if path.is_file() and is_image_file(path):
            image_files.append(path)
    
    return image_files, directory_path

def extract_assistant_response(output):
    """Extract text between 'Assistant:' and 'Prompt:' or end of string."""
    if "Assistant:" not in output:
        return output
    
    # Split on Assistant: and take everything after it
    response = output.split("Assistant:", 1)[1]
    
    # If there's a Prompt: section, remove it and everything after
    if "Prompt:" in response:
        response = response.split("Prompt:", 1)[0]
        
    return "Assistant:" + response.strip()

def analyze_image(image_path):
    """Run image analysis on a single image and return the description."""
    command = [
        "uv", "run",
        "--with", "mlx-vlm",
        "--with", "torch",
        "python", "-m", "mlx_vlm.generate",
        "--model", "mlx-community/SmolVLM-Instruct-bf16",
        "--max-tokens", "500",
        "--temp", "0.0",
        "--prompt", "Describe this image in detail",
        "--image", str(image_path)
    ]
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            return extract_assistant_response(stdout.strip())
        else:
            return f"Error analyzing image: {stderr}"
    except Exception as e:
        return f"Error running analysis: {str(e)}"

@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('num_files', type=int)
@click.option('--output-dir', default='outputs', help='Directory for output files')
def main(directory, num_files, output_dir):
    """Process images from a directory and save descriptions to a JSON file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all image files
    image_files, base_path = find_image_files(directory)
    
    if not image_files:
        click.echo("No image files found in the specified directory.")
        return
    
    # Limit to the specified number of files
    image_files = image_files[:num_files]
    
    # Process images and collect results
    results = []
    for i, image_path in enumerate(image_files, 1):
        click.echo(f"Processing image {i}/{num_files}: {image_path}")
        
        # Get relative path from input directory
        rel_path = image_path.relative_to(base_path)
        
        description = analyze_image(image_path)
        results.append({
            "file": f"./{rel_path}",
            "description": description
        })
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"image_analysis_{timestamp}.json")
    
    # Write results to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=1, ensure_ascii=False)
    
    click.echo(f"\nAnalysis complete. Output saved to: {output_file}")

if __name__ == "__main__":
    main()