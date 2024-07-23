from .NotFoundError import NotFoundError

class NotFoundCustomErrors:
    class UserNotFoundError(NotFoundError):
        def __init__(self, value: str):
            super().__init__(resource="User", value=value, error_code=1010)


    class JobNotFoundError(NotFoundError):
        def __init__(self, value: str):
            super().__init__(resource="Job", value=value, error_code=1020)


    class MatchNotFoundError(NotFoundError):
        def __init__(self, value: str):
            super().__init__(resource="Match", value=value, error_code=1050)


    class FeedbackNotFoundError(NotFoundError):
        def __init__(self, value: str):
            super().__init__(resource="Feedback", value=value, error_code=1040)


    class ResumeNotFoundError(NotFoundError):
        def __init__(self, value: str):
            super().__init__(resource="Resume", value=value, error_code=1030)
    
    class ResourceNotFoundError(NotFoundError):
        def __init__(self, resource: str, value: str):
            super().__init__(resource=resource, value=value, error_code=1000)
