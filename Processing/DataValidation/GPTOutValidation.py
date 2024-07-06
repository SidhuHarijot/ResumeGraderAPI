import json
from .Validation import logError

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
            logError(f"Error validating job description: {job}. \n", e, "JobDescriptionValidation.validate")
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
                return job
            return {
                'title': "",
                'company': "",
                'description': "",
                'required_skills': [],
                'location': "",
                'salary': 0.0,
                'job_type': "",
                'active': True
            }
        except Exception as e:
            logError(f"Error cleaning job description: {job}. \n", e, "JobDescriptionValidation.clean_output")
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
            logError(f"Error validating resume data: {resume}. \n", e, "ResumeDataValidation.validate")
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
            return {
                'uid': " ",
                'skills': [],
                'experience': [],
                'education': []
            }
        except Exception as e:
            logError(f"Error cleaning resume data: {resume}. \n", e, "ResumeDataValidation.clean_output")
            return None


class GradeValidation:
    @classmethod
    def validate(cls, grade, max_grade, total_resumes=None):
        try:
            if isinstance(grade, int):
                if grade < -2 or grade > int(max_grade):
                    return None
                return grade
            elif isinstance(grade, float):
                if grade < -2 or grade > float(max_grade):
                    return None
                return grade
            elif isinstance(grade, list) and all(isinstance(g, int) for g in grade):
                if total_resumes is not None and len(grade) != total_resumes:
                    return None
                if not all(cls.validate(g, max_grade) is not None for g in grade):
                    return None
                return grade
            elif isinstance(grade, list) and all(isinstance(g, float) for g in grade):
                if total_resumes is not None and len(grade) != total_resumes:
                    return None
                if not all(cls.validate(g, max_grade) is not None for g in grade):
                    return None
                return grade
            else:
                return None
        except Exception as e:
            logError(f"Error validating grade: {grade}. \n", e, "GradeValidation.validate")
            return None

    @classmethod
    def clean_output(cls, grade, max_grade, total_resumes=None, response=None):
        try:
            if isinstance(grade, int):
                if cls.validate(grade, max_grade) == None:
                    return -1
                return grade
            elif isinstance(grade, float):
                if not cls.validate(grade, max_grade):
                    return -1.0
                return grade
            elif isinstance(grade, list) and all(isinstance(g, int) for g in grade):
                for i in range(len(grade)):
                    print("validating grade", grade[i], max_grade)
                    if not cls.validate(grade[i], max_grade):
                        print("invalid grade", grade[i])
                        grade[i] = -1
                        print("invalid grade", grade[i])
                if total_resumes is not None and len(grade) != total_resumes:
                    if response is not None:
                        positions_list = [i for i in range(total_resumes)]
                        missing_spots = list(set(positions_list) - set(response.keys()))
                        for spot in missing_spots:
                            grade.insert(spot, -1)
                return grade
            elif isinstance(grade, list) and all(isinstance(g, float) for g in grade):
                for i in range(len(grade)):
                    if not cls.validate(grade[i], max_grade):
                        grade[i] = -1.0
                if total_resumes is not None and len(grade) != total_resumes:
                    if response is not None:
                        positions_list = [i for i in range(total_resumes)]
                        missing_spots = list(set(positions_list) - set(response.keys()))
                        for spot in missing_spots:
                            grade.insert(spot, -1.0)
                return grade
            else:
                return None
        except Exception as e:
            logError(f"Error cleaning grade: {grade}. \n", e, "GradeValidation.clean_output")
            return -1 if isinstance(grade, int) else -1.0 if isinstance(grade, float) else [-1]
