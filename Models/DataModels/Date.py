from pydantic import BaseModel, Field, field_validator


class Date(BaseModel):
    day: int = Field(..., description="Day of the date.")
    month: int = Field(..., description="Month of the date.")
    year: int = Field(..., description="Year of the date.")

    @field_validator('day')
    def day_must_be_valid(cls, v):
        if v == 0:
            return v
        if v < 1 or v > 31:
            raise ValueError('Day must be between 1 and 31')
        return v

    @field_validator('month')
    def month_must_be_valid(cls, v):
        if v == 0:
            return v
        if v < 1 or v > 12:
            raise ValueError('Month must be between 1 and 12')
        return v

    @field_validator('year')
    def year_must_be_valid(cls, v):
        if v < 0 or v > 9999:
            raise ValueError('Year must be between 0 and 9999')
        return v

    def __str__(self):
        return f"{self.day:02d}{self.month:02d}{self.year:04d}"
    
    @classmethod
    def from_string(cls, date_str: str):
        if len(date_str) != 8:
            raise ValueError("Date string must be in DDMMYYYY format")
        day = int(date_str[:2])
        month = int(date_str[2:4])
        year = int(date_str[4:])
        return cls(day=day, month=month, year=year)
    
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

