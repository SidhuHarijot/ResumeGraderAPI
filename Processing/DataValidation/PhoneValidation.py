

class PhoneValidation:
    @staticmethod
    def validate_phone_number(phone_number: str) -> bool:
        if len(phone_number) == 13 and phone_number[2] == "-" and (phone_number[:2] + phone_number[3:]).isnumeric():
            return phone_number
        return None

