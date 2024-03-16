import anthropic
import sys

client = anthropic.Anthropic()

def isEnglish(text):
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.0,
        system="You are a helpful assistant.",
        messages=[
            {"role": "user", "content": f"Is the following phrase in English? Please answer with 'yes' or 'no'.\n\nPhrase: '{text}'"}
            
        ]
    )

    answer = message.content[0].text
    return answer

if __name__ == "__main__":
    # phrase = "IMG_1042"
    # answer = isEnglish(phrase)
    # print(f"Is {phrase} in English? \n{answer}")
    
    if len(sys.argv) < 2:
        print("Please provide a phrase to check. Usage: python language_check.py 'Your phrase here'")
    else:
        text = " ".join(sys.argv[1:])
        print(f"Is '{text}' in English? {isEnglish(text)}")


