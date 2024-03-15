import sys
import os
from openai import OpenAI

client = OpenAI()

def is_english(text):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Update this to the model you intend to use
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Is the following phrase in English? Please answer with 'yes' or 'no'.\n\nPhrase: '{text}'"}
        ]
    )
    answer = completion.choices[0].message.content
    return answer

if __name__ == "__main__":
    # phrase = "IMG_1042"
    # answer = is_english(phrase)
    # print(f"Is {phrase} in English? \n{answer}")
    
    if len(sys.argv) < 2:
        print("Please provide a phrase to check. Usage: python language_check.py 'Your phrase here'")
    else:
        text = " ".join(sys.argv[1:])
        print(f"Is '{text}' in English? {is_english(text)}")
