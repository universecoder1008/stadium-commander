import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
key = os.getenv("GEMINI_API_KEY")

print("Loaded:", key is not None)
print("Length:", len(key) if key else 0)
print("Prefix:", key[:2] if key else None)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate(prompt: str):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text