from .ContentInvalidError import ContentInvalidError


class ContentInvalidCustomErrors:
    class EmailInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Email", value, issue, 1100 )
    
    class UIDInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("UID", value, issue, 1101)
    
    class DateInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Date", value, issue, 1102)
    
    class PhoneInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Phone", value, issue, 1103)
    
    class NameInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Name", value, issue, 1104)
    
    class PrivilegeInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Privilege", value, issue, 1105)
        
    class JobIdInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("JobId", value, issue, 1106)
    
    class SkillsInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Skills", value, issue, 1107)
    
    class ExperienceInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Experience", value, issue, 1108)
    
    class ResumeIdInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("ResumeId", value, issue, 1109)
    
    class EducationInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Education", value, issue, 1110)

    class TitleInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Title", value, issue, 1111)
    
    class EmployerInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Employer", value, issue, 1112)

    class LocationInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Location", value, issue, 1113)
    
    class DescriptionInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Description", value, issue, 1114)
    
    class SalaryInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Salary", value, issue, 1115)
    
    class TypeInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Type", value, issue, 1116)

    class MatchIdInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("MatchId", value, issue, 1117)
    
    class StatusCodeInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("StatusCode", value, issue, 1118)

    class FeedbackIdInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("FeedbackId", value, issue, 1119)
    
    class FeedbackInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Feedback", value, issue, 1120)

    class InstitutionInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Institution", value, issue, 1121)

    class StatusInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Status", value, issue, 1122)

    class GradeInvalid(ContentInvalidError):
        def __init__(self, value: str, issue: str) -> None:
            super().__init__("Grade", value, issue, 1123)
    
