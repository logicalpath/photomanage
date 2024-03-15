import sys
import os
from openai import OpenAI

client = OpenAI()

# Reading OpenAI API key from an environment variable

if not client:
    sys.exit("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")




if __name__ == "__main__":
  completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)  
    
