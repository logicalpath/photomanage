import os
import mlx.core as mx
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config
from typing import List, Union, Dict, Any, Optional
from PIL import Image

class SmolVLM2Helper:
    """
    Helper class for working with SmolVLM2 models.

    SmolVLM2 is the next generation of SmolVLM with enhanced capabilities:
    - Improved math reasoning (51.5 vs 43.9 on MathVista)
    - Better OCR performance (72.9 vs 65.5 on OCRBench)
    - Native video understanding support
    - Enhanced text recognition in photos
    - Better diagram and scientific visual question answering

    Model size: ~5.2GB (vs 500MB for original SmolVLM)
    Architecture: SigLIP image encoder + SmolLM2-1.7B-Instruct
    """

    def __init__(self, model_path: str = "mlx-community/SmolVLM2-2.2B-Instruct-mlx"):
        """
        Initialize the SmolVLM2 helper.

        Args:
            model_path: Path or identifier for the model (default: SmolVLM2-2.2B-Instruct-mlx)
        """
        print(f"Loading SmolVLM2 model from {model_path}...")
        print("Note: First run will download ~5.2GB model to ~/.cache/huggingface/hub/")
        self.model, self.processor = load(model_path)
        self.config = load_config(model_path)
        print("SmolVLM2 model loaded successfully!")

    def describe_image(self,
                       image_path: Union[str, List[str]],
                       prompt: str = "Describe this image in detail.",
                       temp: float = 0.0,
                       max_tokens: int = 100,
                       verbose: bool = False) -> str:
        """
        Generate a description for one or more images.

        SmolVLM2 improvements over original SmolVLM:
        - Better at solving math problems visible in images
        - Improved text recognition (OCR)
        - Enhanced understanding of complex diagrams
        - Better at scientific visual questions

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

    def describe_video(self,
                       video_path: str,
                       prompt: str = "Describe what happens in this video.",
                       temp: float = 0.0,
                       max_tokens: int = 200,
                       verbose: bool = False) -> str:
        """
        Generate a description for a video file.

        NEW in SmolVLM2: Native video understanding capability.

        Note: Requires 'decord' library for video processing.
        Install with: pip install decord

        Args:
            video_path: Path to the video file
            prompt: Text prompt for the model
            temp: Temperature for generation
            max_tokens: Maximum tokens to generate (videos typically need more)
            verbose: Whether to print verbose output

        Returns:
            Generated video description
        """
        try:
            # Format prompt
            formatted_prompt = apply_chat_template(
                self.processor,
                self.config,
                prompt,
                temp=temp,
                max_tokens=max_tokens
            )

            # Generate output for video
            # Note: mlx-vlm should handle video files automatically
            output = generate(
                self.model,
                self.processor,
                formatted_prompt,
                [video_path],
                verbose=verbose
            )

            return output

        except ImportError as e:
            if "decord" in str(e):
                return "Error: Video support requires 'decord' library. Install with: pip install decord"
            raise
        except Exception as e:
            return f"Error processing video: {str(e)}"

    def batch_describe_images(self,
                             directory: str,
                             prompt: str = "Describe this image in detail.",
                             temp: float = 0.0,
                             max_tokens: int = 100,
                             file_types: List[str] = ['.jpg', '.jpeg', '.png', '.arw', '.nef'],
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

    def batch_describe_videos(self,
                             directory: str,
                             prompt: str = "Describe what happens in this video.",
                             temp: float = 0.0,
                             max_tokens: int = 200,
                             file_types: List[str] = ['.mp4', '.mov', '.avi', '.mkv'],
                             max_videos: Optional[int] = None) -> Dict[str, str]:
        """
        Process all videos in a directory and return descriptions.

        NEW in SmolVLM2: Batch video processing capability.

        Args:
            directory: Path to directory containing videos
            prompt: Text prompt for the model
            temp: Temperature for generation
            max_tokens: Maximum tokens to generate
            file_types: List of video file extensions to process
            max_videos: Maximum number of videos to process (None = process all)

        Returns:
            Dictionary mapping video filenames to their descriptions
        """
        results = {}

        # Get all video files in the directory
        video_files = []
        for file in os.listdir(directory):
            if any(file.lower().endswith(ext) for ext in file_types):
                video_files.append(os.path.join(directory, file))

        # Limit the number of videos if specified
        if max_videos is not None:
            video_files = video_files[:max_videos]

        # Process each video
        total_videos = len(video_files)
        for idx, video_path in enumerate(video_files):
            filename = os.path.basename(video_path)
            print(f"Processing video {idx+1}/{total_videos}: {filename}")

            try:
                description = self.describe_video(
                    video_path,
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
    vlm2 = SmolVLM2Helper()

    # Single image example
    # image_path = "/path/to/your/image.jpg"
    # result = vlm2.describe_image(image_path)
    # print(f"\nImage Description: {result}")

    # Video example (NEW in SmolVLM2!)
    # video_path = "/path/to/your/video.mp4"
    # result = vlm2.describe_video(video_path)
    # print(f"\nVideo Description: {result}")

    # Math problem in image (SmolVLM2 is better at this)
    # result = vlm2.describe_image(
    #     "math_problem.jpg",
    #     prompt="Solve the math problem shown in this image and explain your steps.",
    #     max_tokens=300
    # )

    # OCR / Text extraction (SmolVLM2 improved performance)
    # result = vlm2.describe_image(
    #     "document.jpg",
    #     prompt="Extract all text from this image.",
    #     max_tokens=500
    # )

    print("SmolVLM2Helper ready! Uncomment examples above to test.")
