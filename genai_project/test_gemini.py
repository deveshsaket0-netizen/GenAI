# save as test_gemini.py in your project root (same folder as manage.py)
import os
from pathlib import Path
from google import genai

env = {}
for line in Path(".env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

key = env.get("GEMINI_API_KEY")
print(f"Key: {key[:12]}...")

client = genai.Client(api_key=key)
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say hello in one word"
)
print("Response:", response.text)
