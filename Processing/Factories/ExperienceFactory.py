from typing import List
import json
from Models.DataModels.GetModels import *
from .factories import *


class ExperienceFactory:
    @staticmethod
    def to_json(experience: Experience) -> dict:
        try:
            log(f"Converting Experience object to JSON: {experience.title}", "to_json")
            return {
                'start_date': str(experience.start_date),
                'end_date': str(experience.end_date),
                'title': experience.title,
                'company_name': experience.company_name,
                'description': experience.description
            }
        except Exception as e:
            logError(f"Error converting Experience object to JSON: {experience}. \n", e, "to_json")
            raise
    
    @staticmethod
    def from_json(data: dict) -> Experience:
        try:
            if isinstance(data, str):
                data = json.loads(data)
            try:
                log(f"Creating Experience object from JSON: {data['title']} at {data['company_name']}", "from_json")
                return Experience(
                    start_date=Date.create(data['start_date']),
                    end_date=Date.create(data['end_date']),
                    title=data['title'],
                    company_name=data['company_name'],
                    description=data['description']
                )
            except Exception as e:
                logError(f"Error creating Experience object from JSON: {data}. \n", e, "from_json")
                raise
        except Exception as e:
            logError(f"Error creating Experience object from JSON: {data}. \n", e, "from_json")
            raise
    
    @staticmethod
    def bulk_to_json(experiences: List[Experience]) -> List[dict]:
        try:
            log(f"Converting list of Experience objects to JSON: ", "bulk_to_json")
            return [ExperienceFactory.to_json(exp) for exp in experiences]
        except Exception as e:
            logError(f"Error converting list of Experience objects to JSON. \n", e, "to_json")
            raise
    
    @staticmethod
    def build_from_json(data: List[dict]) -> List[Experience]:
        try:
            log(f"Creating list of Experience objects from JSON: ", "build_from_json")
            return [ExperienceFactory.from_json(exp) for exp in data]
        except Exception as e:
            logError(f"Error creating list of Experience objects from JSON. \n", e, "from_json")
            raise
