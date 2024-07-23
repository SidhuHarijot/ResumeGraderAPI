from .services import log, logError
from .WebsocketService import WebsocketService
from .MatchService import MatchService
from .JobService import JobService
from .ResumeService import ResumeService
from Models.RequestModels.GetModels import RequestModels as rm
from Models.DataModels.GetModels import Job, Resume, Match
from Utilities.GetUtilities import OpenAIUtility
from Processing.Factories.GetFactories import ResumeFactory, MatchFactory
from Processing.authorize import authorizeAdmin
import asyncio
from concurrent.futures import ProcessPoolExecutor
import time
from static.CONSTANTS import status_codes

class GradingService(WebsocketService):
    max_grade = 100
    resume_per_request = 10
    grade_codes = [600, 601]

    @authorizeAdmin
    def __init__(self, job_id: int, auth_uid: str):
        self.jobS = JobService.get_from_db(job_id)
        self.matchesS = MatchService.generate_for_job(job_id)
        self.resumes = ResumeService.get_from_job(job_id)
        self.remove_graded_resumes()
        super().__init__()

    def grade_all(self):
        log(f"Grading resumes for job: {self.jobS.job.job_id}", "GradingService.grade_resumes_for_job")
        total_resumes = len(self.resumes)
        job_text = self.jobS.to_text(exclude=["job_id", "active", "location", "application_deadline", "salary", "job_type"])
        for i in range((total_resumes//self.resume_per_request) + 1):
            current_resumes = self.resumes[i*self.resume_per_request:(i+1)*self.resume_per_request]
            resume_texts = [ResumeFactory.to_text(r, exclude=["uid"]) for r in current_resumes]
            grades = OpenAIUtility.grade_resumes(job_text, resume_texts, max_grade=self.max_grade)
            for grade, resume in zip(grades, current_resumes):
                matchS = [m for m in self.matchesS if m.match.uid == resume.uid][0]
                matchS.match.grade = grade
                if grade == -2:
                    code = status_codes.NOT_SUITABLE
                    matchS.match.status = status_codes.get_status(code)
                    matchS.match.status_code = code
                elif grade == -3:
                    code = status_codes.ISSUE_GRADING
                    matchS.match.status = status_codes.get_status(code)
                    matchS.match.status_code = code
                else:
                    code = status_codes.GRADED
                    matchS.match.status = status_codes.get_status(code)
                    matchS.match.status_code = code
                matchS.save_to_db()
            
    def remove_graded_resumes(self):
        log(f"Cleaning resumes for job: {self.jobS.job.job_id}", "GradingService.clean_resumes_for_job")
        total_resumes = len(self.resumes)
        for matchS in self.matchesS:
            if matchS.match.status_code not in self.grade_codes:
                self.matchesS.remove(matchS)
                self.resumes.remove([r for r in self.resumes if r.uid == matchS.match.uid][0])
        log(f"Finished cleaning resumes for job: {self.jobS.job.job_id} removed {total_resumes - len(self.resumes)}", "GradingService.clean_resumes_for_job")

    async def grade_real_time(self):
        log(f"Grading resumes for job: {self.jobS.job.job_id}", "GradingService.grade_resumes_for_job")
        job_text = self.jobS.to_text(exclude=["job_id", "active", "location", "application_deadline", "salary", "job_type"])
        executer = ProcessPoolExecutor()
        loop = asyncio.get_event_loop()
        try:
            split_resumes = [self.resumes[i:i+self.resume_per_request] for i in range(0, len(self.resumes), self.resume_per_request)]
            task_to_resumes = {}
            log(f"Grading resumes for job: {self.jobS.job.job_id} total_batches {len(split_resumes)}", "GradingService.grade_resumes_for_job")
            for resume_batch in split_resumes:
                task = loop.run_in_executor(executer, OpenAIUtility.grade_resumes, job_text, [ResumeFactory.to_text(r, exclude=["uid"]) for r in resume_batch], self.max_grade)
                task_to_resumes[task] = resume_batch
            for task in list(task_to_resumes.keys()):
                grades = await task
                resumes = task_to_resumes[task]
                log(f"Grading resumes for job: {self.jobS.job.job_id} batch {id(task)} result {grades} resumes: {[resume.uid for resume in resumes]}", "GradingService.grade_resumes_for_job")
                for grade, resume in zip(grades, resumes):
                    matchS = [m for m in self.matchesS if m.match.uid == resume.uid][0]
                    matchS.match.grade = grade
                    if grade == -2:
                        code = status_codes.NOT_SUITABLE
                        matchS.match.status = status_codes.get_status(code)
                        matchS.match.status_code = code
                    elif grade == -3:
                        code = status_codes.ISSUE_GRADING
                        matchS.match.status = status_codes.get_status(code)
                        matchS.match.status_code = code
                    else:
                        code = status_codes.GRADED
                        matchS.match.status = status_codes.get_status(code)
                        matchS.match.status_code = code
                    matchS.save_to_db()
                    await self.send_json(MatchFactory.to_json(matchS.match))
        except Exception as e:
            logError("error grading resumes",e, "GradingService.grade_real_time")
            raise e
        finally:
            executer.shutdown()
            log(f"Finished grading resumes for job: {self.jobS.job.job_id}", "GradingService.grade_resumes_for_job")
            
            
