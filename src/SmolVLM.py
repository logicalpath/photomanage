import mlx.core as mx
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config

# Load the model
# model_path = "mlx-community/Qwen2-VL-2B-Instruct-4bit"
model_path = "mlx-community/SmolVLM-Instruct-bf16"

model, processor = load(model_path)
config = load_config(model_path)

# Prepare input
# image = ["http://images.cocodataset.org/val2017/000000039769.jpg"]
image = ["/Users/eddiedickey/workspace/photomanage/database/224x224/9/98fb4fe9-14bd-488b-9553-0cfe810b5808.jpg"]
prompt = "Describe this image in detail."

# Apply chat template
formatted_prompt = apply_chat_template(
    processor, config, prompt, temp=0.0, max_tokens=100
)

# max_tokens = 500  # Define max_tokens with an appropriate value
#   description = generate(model, processor, prompt, pillow_image, temp=0.0, max_tokens=max_tokens, verbose=False)
# Generate output

output = generate(model, processor, formatted_prompt, image, verbose=False)
# output = generate(model, processor, prompt, image, temp=0.0, max_tokens=500, verbose=False)
print(output)


# Prepare input
# image = ["http://images.cocodataset.org/val2017/000000039769.jpg"]
image = ["/Users/eddiedickey/workspace/photomanage/database/224x224/9/981e54b7-d109-47da-b5ab-36a4be95d314.jpg"]
prompt = "Describe this image in detail."

# Apply chat template
formatted_prompt = apply_chat_template(
    processor, config, prompt, temp=0.0, max_tokens=100
)

# max_tokens = 500  # Define max_tokens with an appropriate value
#   description = generate(model, processor, prompt, pillow_image, temp=0.0, max_tokens=max_tokens, verbose=False)
# Generate output

output = generate(model, processor, formatted_prompt, image, verbose=False)
# output = generate(model, processor, prompt, image, temp=0.0, max_tokens=500, verbose=False)
print(output)
