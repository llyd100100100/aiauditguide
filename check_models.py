from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key not found.")
else:
    client = genai.Client(api_key=api_key)
    try:
        print("Listing available models...")
        for m in client.models.list(config={"page_size": 100}):
            if "generateContent" in m.supported_actions:
                print(f"- {m.name} (Display: {m.display_name})")
    except Exception as e:
        print(f"Error listing models: {e}")
