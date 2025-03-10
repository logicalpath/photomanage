import mlx.core as mx
from mlx_vlm import load, generate
from mlx_vlm.utils import load_config
from mlx_vlm.prompt_utils import apply_chat_template

# Load the model
model_path = "mlx-community/SmolVLM-Instruct-bf16"
model, processor = load(model_path)
config = load_config(model_path)

# Process an image
# image_path = "/Users/eddiedickey/workspace/photomanage/test.jpg"
image_path = "./test.jpg"
prompt = "Describe this image in detail."

# Format the prompt with generation parameters
formatted_prompt = apply_chat_template(processor, config, prompt, temp=0.0, max_tokens=100)

# Generate (note the order: formatted_prompt before image)
output = generate(model, processor, formatted_prompt, [image_path], verbose=False)
print(output)
