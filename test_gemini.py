import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

print("API key found:", bool(key))
print("Model:", model)

if not key:
    print("ERROR: Gemini API key is missing")
else:
    try:
        client = genai.Client(api_key=key)

        response = client.models.generate_content(
            model=model,
            contents="Say Hello in Telugu."
        )

        print("Gemini response:")
        print(response.text)

    except Exception as e:
        print("Gemini error type:", type(e).__name__)
        print("Gemini error:", str(e)[:500])