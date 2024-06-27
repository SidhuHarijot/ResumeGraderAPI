from typing import List
import json
from Models.DataModels.GetModels import *
from factories import log, logError


class EducationFactory:
    @staticmethod
    def to_json(education: Education) -> dict:
        try:
            log(f"Converting Education object to JSON: {education.course_name}", "to_json")
            return {
                'start_date': str(education.start_date),
                'end_date': str(education.end_date),
                'institution': education.institution,
                'course_name': education.course_name
            }
        except Exception as e:
            logError(f"Error converting Education object to JSON: {education}. \n", e, "to_json")
            raise
    
    @staticmethod
    def from_json(data: dict) -> Education:
        try:
            log(f"Creating Education object from JSON: {data['course_name']}", "from_json")
            try:
                course_name = data['course_name']
            except TypeError:
                data = json.loads(data)
                course_name = data['course_name']
            return Education(
                start_date=Date.from_string(data['start_date']),
                end_date=Date.from_string(data['end_date']),
                institution=data['institution'],
                course_name=course_name
            )
        except Exception as e:
            logError(f"Error creating Education object from JSON: {data}. \n", e, "from_json")
            raise
    
    @staticmethod
    def bulk_to_json(educations: List[Education]) -> List[dict]:
        try:
            log(f"Converting list of Education objects to JSON: ", "bulk_to_json")
            return [EducationFactory.to_json(edu) for edu in educations]
        except Exception as e:
            logError(f"Error converting list of Education objects to JSON. \n", e, "to_json")
            raise
    
    @staticmethod
    def build_from_json(data: List[dict]) -> List[Education]:
        try:
            log(f"Creating list of Education objects from JSON: ", "build_from_json")
            return [EducationFactory.from_json(edu) for edu in data]
        except Exception as e:
            logError(f"Error creating list of Education objects from JSON. \n", e, "from_json")
            raise
