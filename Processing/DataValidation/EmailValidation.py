import email_validator


class EmailValidation:
    @staticmethod
    def validate_email(email: str) -> bool:
        try:
            validated_email = email_validator.validate_email(email, check_deliverability=False)
            if not validated_email.normalized == email:
                return None
            return validated_email.normalized
        except email_validator.EmailNotValidError:
            return None
