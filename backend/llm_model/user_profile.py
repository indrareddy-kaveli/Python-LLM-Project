import re
from pydantic import BaseModel, Field, EmailStr, field_validator

class UserProfile(BaseModel):
    name: str = Field(min_length = 2)
    age : int = Field(ge = 18, le = 80)
    email : EmailStr
    pan : str
    
    @field_validator("name")
    @classmethod
    def name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        
        return value
    
    @field_validator("pan")
    @classmethod
    def pan(cls, value: str) -> str:
        value = value.strip().upper()
        
        if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value):
            raise ValueError("Invalid PAN format")
        
        return value
        
    
try:
    user = UserProfile(
        name= "John",
        age = 24,
        email = "john@gmail.com",
        pan = "ABCDE1234F"
    )
    
    print("User profile created successfully")
    print(user.model_dump_json(indent = 2))
    
except Exception as error:
    print("User profile creation failed")
    print(error)
    
print("\nTesting Invalid data")
    
try:
    user = UserProfile(
        name = "r",
        age = 12,
        email = "",
        pan = "ABCDE1234F"
    )
    
except Exception as error:
    print(error)    
    print(type(error).__name__)
    