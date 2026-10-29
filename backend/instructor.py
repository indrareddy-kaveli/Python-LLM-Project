
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

sys.path = [
    p for p in sys.path
    if Path(p or os.getcwd()).resolve() != SCRIPT_DIR
]

import instructor
from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ValidationError,
    field_validator,
)

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from the project-root .env")


class UserProfile(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=18, le=100)
    email: EmailStr
    pan: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value):
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value):
            raise ValueError("Invalid PAN format")
        return value


try:
    from groq import Groq

    groq_client = Groq(api_key=api_key)

    client = instructor.from_groq(
        groq_client,
        mode=instructor.Mode.TOOLS,
    )

    profile = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        response_model=UserProfile,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": (
                    "Create a fictional profile for Bunny, age 26, "
                    "email bunny@gmail.com, PAN-format placeholder "
                    "ABCDE1234F."
                ),
            },
        ],
        max_retries=2,
    )

    print("SUCCESS: Structured response generated!")
    print(profile.model_dump_json(indent=2))

except ValidationError as error:
    print("Pydantic validation failed:")
    print(error)

except Exception as error:
    print("LLM request failed:")
    print(f"{type(error).__name__}: {error}")
