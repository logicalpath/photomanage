import mlx.core as mx
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

# Load the model
model_path = "mlx-community/SmolVLM-Instruct-bf16"
model, processor = load(model_path)
config = load_config(model_path)

# Prepare input
image = ["test.jpg"]
prompt = "Describe this image."
max_tokens: int = 500
temp: float = 0.5


# Apply chat template
formatted_prompt = apply_chat_template(
    processor, config, prompt, num_images=len(image)
)

# Generate output
# output = generate(model, processor, image, formatted_prompt, temp=0.5, max_tokens=500, verbose=False)
output = generate(model, processor, image, formatted_prompt, temp=temp, max_tokens=max_tokens, verbose=False)

# output = generate(model, processor, image, formatted_prompt, temp, 500, verbose=False)
print(output)