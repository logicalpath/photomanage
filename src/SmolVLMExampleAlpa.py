import mlx.core as mx
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config
import click
import subprocess
import json
from datetime import datetime
import os
from pathlib import Path
from dataclasses import dataclass
from PIL import Image

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.nef', '.arw'}

@dataclass
class ModelComponents:
    model: any  # You could use a more specific type hint if available
    processor: any
    config: any

def loadModel() -> ModelComponents:
    model_path = "mlx-community/SmolVLM-Instruct-bf16"
    model, processor = load(model_path)
    config = load_config(model_path)
    return ModelComponents(model, processor, config)

# Load the model
model_path = "mlx-community/Qwen2-VL-2B-Instruct-4bit"
model, processor = load(model_path)
config = load_config(model_path)


def analyze_image(image, model, processor, config):

    prompt = "Describe this image in detail"
    click.echo(f"Image path: {image}")

    # Open the image file
    pillow_image = Image.open(image)
    # Generate output
    max_tokens = 500  # Define max_tokens with an appropriate value
    description = generate(model, processor, prompt, pillow_image, temp=0.0, max_tokens=max_tokens, verbose=False)
    # print(output)
    return description



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
    
    # Write image file paths to list_thumbs.txt
    with open('list_thumbs.txt', 'w') as f:
        for image_file in image_files:
            f.write(f"{image_file}\n")

    # Limit to the specified number of files
    image_files = image_files[:num_files]
    
    # Load the model
    components = loadModel()
    model = components.model
    processor = components.processor
    config = components.config

    # Process images and collect results
    results = []
    for i, image_path in enumerate(image_files, 1):
        click.echo(f"Processing image {i}/{num_files}: {image_path}")
        
        # Get relative path from input directory
        rel_path = image_path.relative_to(base_path)
        
        description = analyze_image(str(image_path), model, processor, config)
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


