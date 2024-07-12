from .services import log, logError
from Database.GetDatabases import MatchDatabase
from Models.DataModels.GetModels import Match
from Models.RequestModels.GetModels import RequestModels as rm
from Models.CustomReturnModels.Match import Return as rmReturn
from Processing.Factories.GetFactories import MatchFactory
from Processing.authorize import authorizeAdmin
from .getServices import UserService, JobService


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
        if not self.validate():
            raise ValueError("Invalid match data")
        if not self.match.match_id or self.match.match_id == -1:
            match_id = MatchDatabase.create_match(self.match)
            self.match.match_id = match_id
        else:
            self.update()
    
    def get_return_model(self):
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
        if not self.validate():
            raise ValueError("Invalid match data")
        MatchDatabase.update_match(self.match)
    
    @authorizeAdmin
    def update_from_request(self, request: rm.Matches.Update):
        self.match = request.to_match(self.match)
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
        return result

    @staticmethod
    def generate_for_job(job_id: int):
        matches = MatchDatabase.find({"job_id": job_id})
        matchS = []
        for match in matches:
            matchS.append(MatchService(match))
        return matchS

    @staticmethod
    def clean_match(match):
        return match
    
    def validate(self):
        return True
    
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
    
    

