import os
from dotenv import load_dotenv
from pathlib import Path
from groq import Groq

scripts = Path(__file__).resolve().parent
backend = scripts.parent
load_dotenv(backend / ".env")

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

if not api_key:
    raise ValueError("Groq API key is missing")

if not model:
    raise ValueError("Groq model is missing")

client = Groq(api_key = api_key)

try:    
    response = client.chat.completions.create(
            model = model,
            messages = [
                {
                    "role": "user",
                    "content": "Who is Virat Kohli"
                }
            ],
            temperature = 0
    )
    
    ans = response.choices[0].message.content
    print("Groq API connection successful")
    print("Model:", model)
    print("Response:", ans)
    
except Exception as error:
    print("Groq API connection failed")
    print(type(error).__name__, str(error))