from typing import List
import json
from Models.DataModels.GetModels import *
from .factories import *


class MatchFactory:
    @staticmethod
    def from_db_row(row) -> Match:
        try:
            log(f"Creating Match object from row: {row[1]}", "from_db_row")
            return Match(
                match_id=row[0],
                uid=row[1],
                job_id=row[2],
                status=row[3],
                status_code=row[4],
                grade=row[5],
                selected_skills=row[6]
            )
        except Exception as e:
            logError(f"Error creating Match object from row: {row}. \n", e, "from_db_row")
            raise

    @staticmethod
    def to_db_row(match: Match, with_id=True):
        try:
            log(f"Converting Match object to db row: {match.match_id}", "to_db_row")

            params = (
                match.uid,
                match.job_id,
                match.status,
                match.status_code,
                match.grade,
                match.selected_skills
            )
            if with_id:
                return (match.match_id,) + params
            else:
                return params
        except Exception as e:
            logError(f"Error converting Match object to db row: {match}. \n", e, "to_db_row")
            raise

    @staticmethod
    def from_json(data: dict) -> Match:
        try:
            log(f"Creating Match object from JSON: {data['match_id']}", "from_json")
            if isinstance(data, str):
                data = json.loads(data)
            match = Match.generate_default()
            if 'match_id' in data:
                match.match_id = data['match_id']
            if 'uid' in data:
                match.uid = data['uid']
            if 'job_id' in data:
                match.job_id = data['job_id']
            if 'status' in data:
                match.status = data['status']
            if 'status_code' in data:
                match.status_code = data['status_code']
            if 'grade' in data:
                match.grade = data['grade']
            if 'selected_skills' in data:
                match.selected_skills = data['selected_skills']
            return match
        except Exception as e:
            logError(f"Error creating Match object from JSON: {data}. \n", e, "from_json")
            raise

    @staticmethod
    def to_json(match: Match) -> dict:
        try:
            log(f"Converting Match object to JSON: {match.match_id}", "to_json")
            return {
                'match_id': match.match_id,
                'uid': match.uid,
                'job_id': match.job_id,
                'status': match.status,
                'status_code': match.status_code,
                'grade': match.grade,
                'selected_skills': match.selected_skills
            }
        except Exception as e:
            logError(f"Error converting Match object to JSON: {match}. \n", e, "to_json")
            raise

    @staticmethod
    def from_db_rows(rows: List[tuple]) -> List[Match]:
        try:
            log(f"Creating list of Match objects from multiple rows: ", "from_db_rows")
            return [MatchFactory.from_db_row(row) for row in rows]
        except Exception as e:
            logError(f"Error creating list of Match objects from rows. \n", e, "from_db_rows")
            raise

    @staticmethod
    def to_db_rows(matches: List[Match]) -> List[tuple]:
        try:
            log(f"Converting list of Match objects to db rows: ", "to_db_rows")
            return [MatchFactory.to_db_row(match) for match in matches]
        except Exception as e:
            logError(f"Error converting list of Match objects to db rows. \n", e, "to_db_rows")
            raise

