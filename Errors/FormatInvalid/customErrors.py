from .FormatInvalidError import FormatInvalidError


class FormatInvalidCustomErrors:
    class InvalidEmail(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="email@provider.com") -> None:
            super().__init__("Email", value, recommended_formats, 1200)
    
    class InvalidUID(FormatInvalidError):
        def __init__(self, value, 
                     recommended_formats="1234asfdsda5afsadf6asfdfadfasf") -> None:
            super().__init__("UID", value, recommended_formats, 1201)
    
    class InvalidDate(FormatInvalidError):
        def __init__(self, value, 
                     recommended_formats="{'day': DD, 'month': MM, 'year': YYYY} or DDMMYYYY") -> None:
            super().__init__("Date", value, recommended_formats, 1202)
    
    class InvalidPhone(FormatInvalidError):
        def __init__(self, value, 
                     recommended_formats="01-1234567890") -> None:
            super().__init__("Phone", value, recommended_formats, 1203)

    class InvalidName(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'first_name': 'John', 'last_name': 'Doe'}") -> None:
            super().__init__("Name", value, recommended_formats, 1204)
    
    class InvalidPrivilege(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="'admin'") -> None:
            super().__init__("Privilege", value, recommended_formats, 1205)
    
    class InvalidJobId(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="123") -> None:
            super().__init__("JobId", value, recommended_formats, 1206)
    
    class InvalidSkills(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="['skill1', 'skill2']") -> None:
            super().__init__("Skills", value, recommended_formats, 1207)
    
    class InvalidExperience(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'key': 'value'}") -> None:
            super().__init__("Experience", value, recommended_formats, 1208)

    class InvalidResumeId(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="123") -> None:
            super().__init__("ResumeId", value, recommended_formats, 1209)
    
    class InvalidEducation(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'key': 'value'}") -> None:
            super().__init__("Education", value, recommended_formats, 1210)
    
    class InvalidTitle(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'title': 'value'}") -> None:
            super().__init__("Title", value, recommended_formats, 1211)
    
    class InvalidEmployer(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'employer': 'value'}") -> None:
            super().__init__("Employer", value, recommended_formats, 1212)
    
    class InvalidLocation(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'location': 'value'}") -> None:
            super().__init__("Location", value, recommended_formats, 1213)

    class InvalidDescription(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'description': 'value'}") -> None:
            super().__init__("Description", value, recommended_formats, 1214)
    
    class InvalidSalary(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'salary': 'value'}") -> None:
            super().__init__("Salary", value, recommended_formats, 1215)

    class InvalidType(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'type': 'value'}") -> None:
            super().__init__("Type", value, recommended_formats, 1216)

    class InvalidMatchId(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="123") -> None:
            super().__init__("MatchId", value, recommended_formats, 1217)
    
    class InvalidStatusCode(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'status_code': 'value'}") -> None:
            super().__init__("StatusCode", value, recommended_formats, 1218)
    
    class InvalidFeedbackId(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="123") -> None:
            super().__init__("FeedbackId", value, recommended_formats, 1219)
    
    class InvalidFeedback(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'feedback': 'value'}") -> None:
            super().__init__("Feedback", value, recommended_formats, 1220)
    
    class InvalidInstitution(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'institution': 'value'}") -> None:
            super().__init__("Institution", value, recommended_formats, 1221)

    class InvalidStatus(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'status': 'value'}") -> None:
            super().__init__("Status", value, recommended_formats, 1222)

    class InvalidGrade(FormatInvalidError):
        def __init__(self, value,
                      recommended_formats="{'grade': 'value'}") -> None:
            super().__init__("Grade", value, recommended_formats, 1223)
