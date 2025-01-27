import subprocess
import sys
from datetime import datetime
import os

def run_image_analysis(image_path, output_dir="outputs"):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"image_analysis_{timestamp}.txt")
    
    # Construct the command
    command = [
        "uv", "run",
        "--with", "mlx-vlm",
        "--with", "torch",
        "python", "-m", "mlx_vlm.generate",
        "--model", "mlx-community/SmolVLM-Instruct-bf16",
        "--max-tokens", "500",
        "--temp", "0.5",
        "--prompt", "Describe this image in detail",
        "--image", image_path
    ]
    
    try:
        # Run the command and capture output
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        # Write output to file
        with open(output_file, 'w') as f:
            f.write("=== Image Analysis Output ===\n")
            f.write(f"Image: {image_path}\n")
            f.write(f"Time: {timestamp}\n")
            f.write("\n=== Standard Output ===\n")
            f.write(stdout)
            if stderr:
                f.write("\n=== Standard Error ===\n")
                f.write(stderr)
        
        print(f"Analysis complete. Output saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error running analysis: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    run_image_analysis(image_path)