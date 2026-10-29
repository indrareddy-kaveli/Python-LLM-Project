
import re
from pydantic import BaseModel, Field, EmailStr, ValidationError, field_validator


class UserProfile(BaseModel):
    name: str = Field(min_length=2)
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

        pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

        if not re.fullmatch(pattern, value):
            raise ValueError(
                "PAN must contain 5 letters, 4 digits, and 1 letter "
                "(example format: ABCDE1234F)"
            )

        return value


valid_data = {
    "name": "Rahul",
    "age": 25,
    "email": "rahul@gmail.com",
    "pan": "ABCDE1234F"
}

try:
    user = UserProfile(**valid_data)

    print("VALIDATION SUCCESSFUL")
    print(user.model_dump())

except ValidationError as error:
    print("Validation failed:")
    print(error)


invalid_data = {
    "name": "   ",
    "age": 15,
    "email": "invalid-email",
    "pan": "ABC123"
}

print("\nTesting invalid data...")

try:
    user = UserProfile(**invalid_data)
    print(user.model_dump())

except ValidationError as error:
    print("VALIDATION ERROR CAUGHT")
    for issue in error.errors():
        field = ".".join(str(part) for part in issue["loc"])
        print(f"Field: {field} | Error: {issue['msg']}")
