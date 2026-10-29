
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from intent_detection import detect_intent

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent

load_dotenv(BACKEND_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env")

if not model:
    raise ValueError("GROQ_MODEL is missing from .env")

client = Groq(api_key=api_key)


def generate_response(message: str, history : list | None=None) -> str:
    intent = detect_intent(message)

    instructions = {
        "greeting": "Reply with a friendly greeting.",
        "question": "Answer the user's question clearly.",
        "explanation": "Explain the topic in simple words with an example.",
        "summarization": "Summarize the supplied text using the main points.",
        "general": "Respond helpfully to the user's message."
    }

    system_prompt = (
        "You are a helpful AI assistant. "
        "Use the conversation history to answer follow-up questions. "
        + instructions.get(
            intent,
            "Respond helpfully to the user's message."
        )
    )
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    
    if history:
        for item in history[-6:]:
            if item.get("role") in ("user", "assistant"):
                content = item.get("content")

                if isinstance(content, str) and content.strip():
                    messages.append({
                        "role": item["role"],
                        "content": content[:1000]
                    })

        
    messages.append({
        "role": "user",
        "content": message
    })

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )

    answer = response.choices[0].message.content

    return answer or "Sorry, I couldn't generate a response."


if __name__ == "__main__":
    user_message = input("Enter your message: ")

    try:
        answer = generate_response(user_message)
        print("\nAI response:")
        print(answer)

    except Exception as error:
        print("Something went wrong:")
        print(type(error).__name__, str(error))
