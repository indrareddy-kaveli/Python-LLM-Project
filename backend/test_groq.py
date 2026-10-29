
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. Check your .env file."
    )

client = Groq(api_key=api_key)

try:
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        messages=[
            {
                "role": "user",
                "content": (
                    "Who is Virat Kohli? Provide a brief summary of his cricket career."
                ),
            }
        ],
    )

    print("SUCCESS: Groq API connected!")
    print("\nLLM Response:")
    print(response.choices[0].message.content)

except Exception as error:
    print("Groq API request failed.")
    print(type(error).__name__, str(error))
