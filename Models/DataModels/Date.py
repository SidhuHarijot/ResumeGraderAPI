from pydantic import BaseModel, Field, field_validator
import time
from Errors.GetErrors import Errors as e
from .logs import log, logError


class Date(BaseModel):
    day: int = Field(..., description="Day of the date.")
    month: int = Field(..., description="Month of the date.")
    year: int = Field(..., description="Year of the date.")

    @field_validator('day')
    def day_must_be_valid(cls, v):
        if v == 0:
            return v
        if v < 1 or v > 31:
            logError("Day value out of bounds.", e.ContentInvalid.DateInvalid(v, "Day must be between 1 and 31"), "Date")
            return 0
        return v

    @field_validator('month')
    def month_must_be_valid(cls, v):
        if v == 0:
            return v
        if v < 1 or v > 12:
            logError("Month value out of bounds.", e.ContentInvalid.DateInvalid(v, 'Month must be between 1 and 12'), "Date")
            return 0
        return v

    @field_validator('year')
    def year_must_be_valid(cls, v):
        if v < 0 or v > 9999:
            logError("Year value out of Bounds", e.ContentInvalid.DateInvalid(v, 'Year must be between 0 and 9999'), "Date")
            return 0
        return v

    def __str__(self):
        return f"{self.day:02d}{self.month:02d}{self.year:04d}"
    
    @classmethod
    def from_string(cls, date_str: str):
        if len(date_str) != 8:
            raise e.FormatInvalid.InvalidDate(date_str)
        day = int(date_str[:2])
        month = int(date_str[2:4])
        year = int(date_str[4:])
        return cls(day=day, month=month, year=year)
    
    @classmethod
    def from_json(cls, data: dict):
        if data['dob']:
            if isinstance(data["dob"], str):
                return cls.from_string(data["dob"])
            return cls(day=data['dob']['day'], month=data['dob']['month'], year=data['dob']['year'])
        elif data['day'] and data['month'] and data['year']:
            return cls(day=data['day'], month=data['month'], year=data['year'])
        else:
            raise e.FormatInvalid.InvalidDate(data)
    
    @classmethod
    def create(cls, data):
        if isinstance(data, dict):
            return cls.from_json(data)
        return cls.from_string(data)\
    
    def display(self):
        return f"[{self.day:02d}/{self.month:02d}/{self.year:04d}]"
    
    @staticmethod
    def today():
        today = time.localtime()
        return Date(day=today.tm_mday, month=today.tm_mon, year=today.tm_year)
    
    def __eq__(self, value: object) -> bool:
        return self.day == value.day and self.month == value.month and self.year == value.year
    
    def __ne__(self, value: object) -> bool:
        return self.day != value.day or self.month != value.month or self.year != value.year
    
    def __lt__(self, value: object) -> bool:
        return self.year < value.year and self.month < value.month and self.day < value.day

    def __le__(self, value: object) -> bool:
        return self.year <= value.year and self.month <= value.month and self.day <= value.day
    
    def __gt__(self, value: object) -> bool:
        return self.year > value.year and self.month > value.month and self.day > value.day
    
    def __ge__(self, value: object) -> bool:
        return self.year >= value.year and self.month >= value.month and self.day >= value.day

