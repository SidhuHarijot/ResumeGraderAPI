from .database import Database


class Exists(Database):
    @classmethod
    def job(cls, job_id: int=None) -> bool:
        return cls.has("jobdescriptions", ["job_id"], [job_id])
    
    @classmethod
    def user(cls, uid: str=None, email: str=None, phone_no: str=None) -> bool:
        columns = []
        values = []
        if uid:
            columns.append("uid")
            values.append(uid)
        if email:
            columns.append("email")
            values.append(email)
        if phone_no:
            columns.append("phone_no")
            values.append(phone_no)
        return cls.has("users", columns, values)
    
    @classmethod
    def match(cls, match_id: int=None, uid: str=None, job_id: int=None) -> bool:
        columns = []
        values = []
        if match_id:
            columns.append("match_id")
            values.append(match_id)
        if uid:
            columns.append("uid")
            values.append(uid)
        if job_id:
            columns.append("job_id")
            values.append(job_id)
        return cls.has("matches", columns, values)
    
    @classmethod
    def feedback(cls, feedback_id: int=None, match_id: int=None, auth_uid: str=None) -> bool:
        columns = []
        values = []
        if feedback_id:
            columns.append("feedback_id")
            values.append(feedback_id)
        if match_id:
            columns.append("match_id")
            values.append(match_id)
        if auth_uid:
            columns.append("auth_uid")
            values.append(auth_uid)
        return cls.has("feedback", columns, values)
