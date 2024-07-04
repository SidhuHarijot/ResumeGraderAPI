from .Feedback import Create as FeedbackCreate, Update as FeedbackUpdate, Get as FeedbackGet
from .User import Create as UserCreate, Update as UserUpdate
from .UserPrivileges import Update as UserPrivilegesUpdate
from .Resumes import Create as ResumeCreate, Update as ResumeUpdate
from .Matches import Create as MatchCreate, Get as MatchGet, Update as MatchUpdate
from .Jobs import Create as JobCreate, Update as JobUpdate, Get as JobGet

class RequestModels:
    class User:
        class Create(UserCreate):
            pass

        class Update(UserUpdate):
            pass

        class Privileges:
            class Update(UserPrivilegesUpdate):
                pass


    class Resumes:
        class Create(ResumeCreate):
            pass

        class Update(ResumeUpdate):
            pass


    class Matches:
        class Create(MatchCreate):
            pass

        class Get(MatchGet):
            pass

        class Update(MatchUpdate):
            pass


    class Jobs:
        class Create(JobCreate):
            pass

        class Update(JobUpdate):
            pass

        class Get(JobGet):
            pass


    class Feedback:
        class Create(FeedbackCreate):
            pass

        class Update(FeedbackUpdate):
            pass

        class Get(FeedbackGet):
            pass
