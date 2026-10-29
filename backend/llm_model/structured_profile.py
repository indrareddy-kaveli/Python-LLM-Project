import os
import re
from pydantic import BaseModel, Field, EmailStr, field_validator
from pathlib import Path
from dotenv import load_dotenv
import instructor

script = Path(__file__).resolve().parent
backend = script.parent
load_dotenv(backend/".env")

class Profile(BaseModel):
    name: str = Field(min_length = 2)
    age : int = Field(ge = 18, le = 80)
    email: EmailStr
    pan: str
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value : str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Name must contain atleast 2 characters")
        
        return value
    
    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value: str) -> str:
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value):
            raise ValueError("Invalid Pan Format")
        
        return value
    
api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

if not api_key:
    raise ValueError("GROQ API key is missing")

if not model:
    raise ValueError("GROQ_MODEL is missing")

if not model.startswith("groq/"):
    model = f"groq/{model}"

try:
    client = instructor.from_provider(
        model = model,
        api_key = api_key,
        mode = instructor.Mode.TOOLS
    )
    
    user = client.create(
        response_model = Profile,
        messages=[
            {
                "role": "user",
                "content":(
                    "Create a fictional example user profile."
                    "Use a name and age between 18 and 80"
                    "a correctly formatted example email"
                    "a fictinal pan-format string"
                    "Do not claim the details belong to real person"
                )
            }
        ]
    )
    print("Structure response generated")
    print(user.model_dump_json(indent = 2))

except Exception as error:
    print("Structured response generation failed")
    print(type(error).__name__, str(error))        