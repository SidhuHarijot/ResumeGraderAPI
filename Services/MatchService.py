from .services import log, logError
from Database.GetDatabases import MatchDatabase
from Models.DataModels.GetModels import Match
from Models.RequestModels.GetModels import RequestModels as rm
from Models.CustomReturnModels.Match import Return as rmReturn
from Processing.Factories.GetFactories import MatchFactory
from Processing.authorize import authorizeAdmin
from static.CONSTANTS import status_codes
from Database.check import Exists
from Errors.GetErrors import Errors as e
from .UserService import UserService


class MatchService:
    match: Match = None
    return_model: rmReturn= None

    def __init__(self, match: Match=None, dict: dict=None, json_str: str=None, db_row: str=None):
        if dict or json_str:
            match = MatchFactory.from_json(dict)
        elif db_row:
            match = MatchFactory.from_db_row(db_row)
        if match:
            self.match = match
            
        else:
            raise ValueError("No valid arguments provided to MatchService constructor")
    
    def save_to_db(self):
        self.validate()
        if not self.match.match_id or self.match.match_id == -1:
            match_id = MatchDatabase.create_match(self.match)
            self.match.match_id = match_id
        else:
            self.update()
    
    @classmethod
    def put_for_re_evaluation(cls, uid: str=None, job_id: int = None):
        matches = []
        if uid:
            matches = cls.get_from_request(rm.Matches.Get(uid=uid), return_type=MatchService)
        elif job_id:
            matches = cls.get_from_request(rm.Matches.Get(job_id=job_id), return_type=MatchService)
        for match in matches:
            match.match.status = status_codes.get_status(status_codes.PENDING_RE_EVALUATION)
            match.match.status_code = status_codes.PENDING_RE_EVALUATION
            match.match.grade = 0.0
            match.update()
            
    def get_return_model(self):
        from .JobService import JobService
        if not self.return_model:
            self.return_model = rmReturn(
                match_id = self.match.match_id,
                uid = self.match.uid,
                job_id = self.match.job_id,
                status = self.match.status,
                status_code = self.match.status_code,
                grade = self.match.grade,
                selected_skills = self.match.selected_skills,
                user = UserService.get_from_db(self.match.uid).user,
                job = JobService.get_from_db(self.match.job_id).job
            )
        return self.return_model
    
    @staticmethod
    def create_from_request(request: rm.Matches.Create):
        matchS = MatchService(request.to_match())
        matchS.save_to_db()
        return matchS
    
    def update(self):
        self.validate()
        MatchDatabase.update_match(self.match)
    
    @authorizeAdmin
    def update_from_request(self, request: rm.Matches.Update):
        author = UserService.get_from_db(request.auth_uid).user
        name = author.name.first_name[:1] + " " + author.name.last_name
        self.match = request.to_match(self.match, name)
        self.update()
    
    @staticmethod
    def get_from_db(match_id: int):
        return MatchService(MatchDatabase.get_match(match_id))
    
    def to_json(self):
        return MatchFactory.to_json(self.match)
    
    @staticmethod
    def get_from_request(request: rm.Matches.Get, return_type=Match):
        matches = MatchDatabase.find(request.get_find_params())
        result = []
        log(f"return type == {return_type} type == rmReturn > {issubclass(return_type, rmReturn)}", "MatchService.get_from_request")
        for match in matches:
            if issubclass(return_type, rmReturn):
                result.append(MatchService(match).get_return_model())
            elif issubclass(return_type, Match):
                result.append(MatchService.clean_match(match))
            elif issubclass(return_type, MatchService):
                result.append(MatchService(match))
        return result

    @staticmethod
    def generate_for_job(job_id: int):
        matches = MatchDatabase.find({"job_id": job_id})
        matchS = []
        for match in matches:
            matchS.append(MatchService(match))
        return matchS

    
    def validate(self):
        if not self.match.uid or not Exists.user(self.match.uid):
            self.match.uid = "None" if not self.match.uid else self.match.uid
            raise e.ContentInvalid.UIDInvalid(self.match.uid, f"User does not exist")
        if not self.match.job_id or not Exists.job(self.match.job_id):
            self.match.job_id = -1 if not self.match.job_id else self.match.job_id
            raise e.ContentInvalid.JobIdInvalid(self.match.job_id, "Job does not exist")
        if not self.match.status_code in status_codes.get_all_codes():
            self.match.status_code = status_codes.APPLIED
            self.match.status = status_codes.get_status(status_codes.APPLIED)
    
    def delete(self):
        MatchDatabase.delete_match(self.match.match_id)
    
    @staticmethod
    def delete_from_db(match_id: int):
        MatchDatabase.delete_match(match_id)
    
    @staticmethod
    @authorizeAdmin
    def print_all(request):
        matches = MatchDatabase.get_all_matches()
        html_data = """
        <html>
        <head>
        <style>
        table {
          font-family: Arial, sans-serif;
          border-collapse: collapse;
          width: 100%;
        }
        
        td, th {
          border: 1px solid #dddddd;
          text-align: left;
          padding: 8px;
        }
        
        tr:nth-child(even) {
          background-color: #dddddd;
        }
        
        th {
          background-color: #f2f2f2;
        }
        
        h1 {
          text-align: center;
        }
        
        </style>
        <title>All Matches</title>
        </head>

        <body>
        <h1>All Matches</h1>
        <table>
        <tr>
        <th>Match ID</th>
        <th>UID</th>
        <th>Job ID</th>
        <th>Status</th>
        <th>Status Code</th>
        <th>Grade</th>
        <th>Selected Skills</th>
        </tr>
        """
        for match in matches:
            html_data += f"""
            <tr>
            <td>{match.match_id}</td>
            <td>{match.uid}</td>
            <td>{match.job_id}</td>
            <td>{match.status}</td>
            <td>{match.status_code}</td>
            <td>{match.grade}</td>
            <td>{", <br>".join([m for m in match.selected_skills])}</td>
            </tr>
            """
        html_data += """
        </table>
        </body>
        </html>
        """
        return html_data
    
    

