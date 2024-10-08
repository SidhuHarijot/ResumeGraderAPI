from typing import List
import json
from Models.DataModels.GetModels import *
from .ExperienceFactory import ExperienceFactory
from .EducationFactory import EducationFactory
from .factories import log, logError


class ResumeFactory:
    @staticmethod
    def from_db_row(row) -> Resume:
        try:
            log(f"Creating Resume object from row: {row[1]}", "from_db_row")
            return Resume(
                uid=row[0],
                skills=row[1],
                experience=ExperienceFactory.build_from_json(row[2]),
                education=EducationFactory.build_from_json(row[3])
            )
        except Exception as e:
            logError(f"Error creating Resume object from row: {row}. \n", e, "from_db_row")
            raise

    @staticmethod
    def to_db_row(resume: Resume, with_uid=True) -> tuple:
        try:
            log(f"Converting Resume object to db row: {resume.uid}", "to_db_row")
            params = (resume.skills, json.dumps(ExperienceFactory.bulk_to_json(resume.experience)),
                      json.dumps(EducationFactory.bulk_to_json(resume.education)))
            if with_uid:
                return (resume.uid,) + params
            return params
        except Exception as e:
            logError(f"Error converting Resume object to db row: {resume}. \n", e, "to_db_row")
            raise

    @staticmethod
    def from_json(data: dict) -> Resume:
        try:
            log(f"Creating Resume object from JSON: {data['uid']}", "from_json")
            try:
                uid = data.get('uid', "UID")
            except TypeError:
                data = json.loads(data)
                uid = data.get('uid', "UID")
            return Resume(
                uid=uid,
                skills=data['skills'],
                experience=ExperienceFactory.build_from_json(data['experience']),
                education=EducationFactory.build_from_json(data['education'])
            )
        except Exception as e:
            logError(f"Error creating Resume object from JSON: {data}. \n", e, "from_json")
            raise

    @staticmethod
    def to_json(resume: Resume) -> dict:
        try:
            log(f"Converting Resume object to JSON: {resume.uid}", "to_json")
            return {
                'uid': resume.uid,
                'skills': resume.skills,
                'experience': ExperienceFactory.bulk_to_json(resume.experience),
                'education': EducationFactory.bulk_to_json(resume.education)
            }
        except Exception as e:
            logError(f"Error converting Resume object to JSON: {resume}. \n", e, "to_json")
            raise

    @staticmethod
    def from_db_rows(rows: List[tuple]) -> List[Resume]:
        try:
            log(f"Creating list of Resume objects from rows: ", "from_db_rows")
            return [ResumeFactory.from_db_row(row) for row in rows]
        except Exception as e:
            logError(f"Error creating list of Resume objects from rows. \n", e, "from_db_rows")
            raise

    @staticmethod
    def to_db_rows(resumes: List[Resume]) -> List[tuple]:
        try:
            log(f"Converting list of Resume objects to db rows: ", "to_db_rows")
            return [ResumeFactory.to_db_row(resume) for resume in resumes]
        except Exception as e:
            logError(f"Error converting list of Resume objects to db rows. \n", e, "to_db_rows")
            raise
    
    @staticmethod
    def to_text(resume: Resume, exclude: List[str]) -> str:
        try:
            log(f"Converting Resume object to text: {resume.uid}", "to_text")
            resume = ResumeFactory.to_json(resume)
            text = ""
            for key, value in resume.items():
                if key not in exclude:
                    text += f"{key}: {value}\n||"
            return text
        except Exception as e:
            logError(f"Error converting Resume object to text: {resume}. \n", e, "to_text")
            raise
