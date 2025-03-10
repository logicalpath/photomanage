import os
import mlx.core as mx
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config
from typing import List, Union, Dict, Any, Optional
from PIL import Image

class SmolVLMHelper:
    """
    Helper class for working with SmolVLM models.
    Handles loading, image processing, and generation with proper parameter ordering.
    """
    
    def __init__(self, model_path: str = "mlx-community/SmolVLM-Instruct-bf16"):
        """
        Initialize the SmolVLM helper.
        
        Args:
            model_path: Path or identifier for the model
        """
        print(f"Loading model from {model_path}...")
        self.model, self.processor = load(model_path)
        self.config = load_config(model_path)
        print("Model loaded successfully!")
        
    def describe_image(self, 
                       image_path: Union[str, List[str]], 
                       prompt: str = "Describe this image in detail.",
                       temp: float = 0.0,
                       max_tokens: int = 100,
                       verbose: bool = False) -> str:
        """
        Generate a description for one or more images.
        
        Args:
            image_path: Path to the image or list of image paths
            prompt: Text prompt for the model
            temp: Temperature for generation (lower = more deterministic)
            max_tokens: Maximum number of tokens to generate
            verbose: Whether to print verbose output
            
        Returns:
            Generated description(s)
        """
        # Handle single image path vs list of paths
        if isinstance(image_path, str):
            image_paths = [image_path]
        else:
            image_paths = image_path
            
        # Apply chat template with generation parameters
        formatted_prompt = apply_chat_template(
            self.processor, 
            self.config, 
            prompt, 
            temp=temp,
            max_tokens=max_tokens
        )
        
        # Generate output - NOTE ORDER: formatted_prompt comes before image
        output = generate(
            self.model, 
            self.processor, 
            formatted_prompt, 
            image_paths, 
            verbose=verbose
        )
        
        return output
    
    def batch_describe_images(self, 
                             directory: str, 
                             prompt: str = "Describe this image in detail.",
                             temp: float = 0.0,
                             max_tokens: int = 100,
                             file_types: List[str] = ['.jpg', '.jpeg', '.png'],
                             max_images: Optional[int] = None) -> Dict[str, str]:
        """
        Process all images in a directory and return descriptions.
        
        Args:
            directory: Path to directory containing images
            prompt: Text prompt for the model
            temp: Temperature for generation
            max_tokens: Maximum tokens to generate
            file_types: List of file extensions to process
            max_images: Maximum number of images to process (None = process all)
            
        Returns:
            Dictionary mapping image filenames to their descriptions
        """
        results = {}
        
        # Get all image files in the directory
        image_files = []
        for file in os.listdir(directory):
            if any(file.lower().endswith(ext) for ext in file_types):
                image_files.append(os.path.join(directory, file))
        
        # Limit the number of images if specified
        if max_images is not None:
            image_files = image_files[:max_images]
            
        # Process each image
        total_images = len(image_files)
        for idx, image_path in enumerate(image_files):
            filename = os.path.basename(image_path)
            print(f"Processing image {idx+1}/{total_images}: {filename}")
            
            try:
                description = self.describe_image(
                    image_path, 
                    prompt=prompt,
                    temp=temp,
                    max_tokens=max_tokens
                )
                results[filename] = description
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                results[filename] = f"Error: {str(e)}"
                
        return results

# Example usage
if __name__ == "__main__":
    # Initialize the helper
    vlm = SmolVLMHelper()
    
    # Single image example
    image_path = "/path/to/your/image.jpg"
    result = vlm.describe_image(image_path)
    print(f"\nDescription: {result}")
    
    # Directory processing example
    # results = vlm.batch_describe_images("/path/to/images/directory", max_images=5)
    # for filename, description in results.items():
    #     print(f"\n{filename}:\n{description}")
