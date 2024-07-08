from pydantic import BaseModel, Field, field_validator
import re


NAME_PATTERN = '^[a-zA-Z\s\-]+$'

class Name(BaseModel):
    first_name: str = Field(..., description="First name of the user.")
    last_name: str = Field(..., description="Last name of the user.")

    @field_validator('first_name')
    def first_name_must_be_valid(cls, v):
        if len(v) < 2 or len(v) > 50:
            raise ValueError('First name must be between 2 and 50 characters')
        if re.match(NAME_PATTERN, v) is None:
            raise ValueError('First name contains invalid characters')
        return v
    
    @field_validator('last_name')
    def last_name_must_be_valid(cls, v):
        if len(v) < 2 or len(v) > 50:
            raise ValueError('Last name must be between 2 and 50 characters')
        if re.match(NAME_PATTERN, v) is None:
            raise ValueError('Last name contains invalid characters')
        return v
    
    def __str__(self):
        return f"[({self.first_name}), ({self.last_name})]"
    
    @classmethod
    def from_string(cls, name_str: str):
        if len(name_str) < 2 or len(name_str) > 100:
            raise ValueError("Name string must be between 2 and 100 characters")
        first_name = name_str[2: name_str.index(')')]
        last_name = name_str[name_str.index('(', 2) + 1: -2]
        return cls(first_name=first_name, last_name=last_name)

    @classmethod
    def from_json(cls, data: dict):
        if data['name']:
            if isinstance(data["name"], str):
                return cls.from_string(data["name"])
            return cls(first_name=data['name']['first_name'], last_name=data['name']['last_name'])
        elif data['first_name'] and data['last_name']:
            return cls(first_name=data['first_name'], last_name=data['last_name'])
        else:
            raise ValueError("Name data is not valid")
        

    @classmethod
    def create(cls, data):
        if isinstance(data, dict):
            return cls.from_json(data)
        return cls.from_string(data)

