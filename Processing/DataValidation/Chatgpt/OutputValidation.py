import json
from Processing.DataValidation.Validation import log, logError

class JobDescriptionValidation:
    @staticmethod
    def validate(job):
        try:
            job_json = None
            if isinstance(job, str):
                job_json = json.loads(job)
            elif isinstance(job, dict):
                job_json = job
            if job_json:
                if not job_json['title'] or not isinstance(job_json['title'], str):
                    return None
                if not job_json['company'] or not isinstance(job_json['company'], str):
                    return None
                if not job_json['description'] or not isinstance(job_json['description'], str):
                    return None
                if not all(isinstance(skill, str) for skill in job_json['required_skills']):
                    return None
                if not job_json['location'] or not isinstance(job_json['location'], str):
                    return None
                if not isinstance(job_json['salary'], float):
                    return None
                if job_json['job_json_type'] not in ['FULL', 'PART', 'CONT', 'UNKN']:
                    return None
                if not isinstance(job_json['active'], bool):
                    return None
                return job
            return None
        except Exception as e:
            logError(f"Error validating job description: {job}. \n", e, "validate")
            return None
    
    @staticmethod
    def clean_output(job) -> dict:
        try:
            if isinstance(job, str):
                job = json.loads(job)
            if isinstance(job, dict):
                if not job['title'] or not isinstance(job['title'], str):
                    job['title'] = " "
                if not job['company'] or not isinstance(job['company'], str):
                    job['company'] = " "
                if not job['description'] or not isinstance(job['description'], str):
                    job['description'] = " "
                if not all(isinstance(skill, str) for skill in job['required_skills']):
                    job['required_skills'] = [skill for skill in job['required_skills'] if isinstance(skill, str) and skill]
                if not job['location'] or not isinstance(job['location'], str):
                    job['location'] = " "
                if not isinstance(job['salary'], float):
                    job['salary'] = 0.0
                if job['job_type'] not in ['FULL', 'PART', 'CONT', 'UNKN']:
                    job['job_type'] = "UNKN"
                if not isinstance(job['active'], bool):
                    job['active'] = True
                return job
            return None
        except Exception as e:
            logError(f"Error cleaning job description: {job}. \n", e, "clean_output")
            return None


class ResumeDataValidation:
    @staticmethod
    def validate(resume):
        try:
            resume_json = None
            if isinstance(resume, str):
                resume_json = json.loads(resume)
            elif isinstance(resume, dict):
                resume_json = resume
            if resume_json:
                if not resume_json['uid'] or resume_json['uid'] != -1:
                    return None
                if not all(isinstance(skill, str) for skill in resume_json['skills']):
                    return None
                if not all(isinstance(experience, dict) for experience in resume_json['experience']):
                    return None
                if not all(isinstance(education, dict) for education in resume_json['education']):
                    return None
                return resume
        except Exception as e:
            logError(f"Error validating resume data: {resume}. \n", e, "validate")
            return None
    
    @staticmethod
    def clean_output(resume):
        try:
            if isinstance(resume, str):
                resume = json.loads(resume)
            if isinstance(resume, dict):
                if not resume['uid'] or resume['uid'] != -1:
                    resume['uid'] = " "
                if not all(isinstance(skill, str) for skill in resume['skills']):
                    resume['skills'] = [skill for skill in resume['skills'] if isinstance(skill, str) and skill]
                if not all(isinstance(experience, dict) for experience in resume['experience']):
                    resume['experience'] = [experience for experience in resume['experience'] if isinstance(experience, dict)]
                if not all(isinstance(education, dict) for education in resume['education']):
                    resume['education'] = [education for education in resume['education'] if isinstance(education, dict)]
                return resume
            return None
        except Exception as e:
            logError(f"Error cleaning resume data: {resume}. \n", e, "clean_output")
            return None

