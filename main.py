from fastapi import FastAPI, File, UploadFile
from mangum import Mangum
from pydantic import BaseModel, model_validator
from openai import OpenAI
import PyPDF2 as pypdf2
import docx2txt


class GradeRequestData(BaseModel):
    resumeData: dict[int, str]
    jobDescription:str
    noOfResumes: int
    apiKey: str

    @model_validator(mode="after")
    def checkResumeCount(self):
        if len(self.resumeData) != self.noOfResumes:
            raise ValueError("No of resumes does not match the number of resume data provided in the resumeData")
        return self


app = FastAPI()
handler = Mangum(app)

@app.get("/")
def read_root():
    return {"version": "1.0",
            "author": "Harijot Singh",
            "Title": "Resume Grader",
            "Description": "This is an API to grade resumes for a provided job description."}


@app.post("/grade/ChatGPT/{maxGrade}")
async def grade_chatgpt(maxGrade: int, requestData: GradeRequestData):
    """
    grades resumes using ChatGPT model.
    Args:
    - maxGrade (int): The maximum possible grade.
    - requestData (GradeRequestData): The request data containing the resume data and job description.

    Returns:
    - dict: A dictionary containing the grades for each resume and an error log.
    """
    grades: dict[int, int] = {}
    errorLog = {}
    ids = [*requestData.resumeData.keys()]
    resumeData = [*requestData.resumeData.values()]
    response = await _grade_resume_chatGPT(requestData.apiKey, requestData.jobDescription, resumeData, maxGrade)
    for i in range(len(ids)):
        if "Error: " not in response[i]:
            grades[ids[i]] = int(response[i])
        else:
            errorLog[ids[i]] = response[i]
    return {"Grades" : grades, "errorLog": errorLog}


async def _grade_resume_chatGPT(api_key, jobDescription, resumeList, maxGrade):
    """
    Grades a resume based on a job description using GPT-4.
    
    Args:
    - api_key (str): The API key for authenticating with the OpenAI API.
    - jobDescription (str): System description, e.g., "Grade resumes for a Software Engineer position. Maximum grade: 100."
    - resumeList (List[str]): List of resumes
    - maxGrade (int): The maximum possible grade.

    Returns:
    - List[str]: A list of grades for each resume.
    """

    client = OpenAI(api_key=api_key, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")
    grades = []

    systemString = f"Grade resumes for this job description: \"{jobDescription}\" Maximum grade is {maxGrade}. " + \
                   "Just answer in the number or the grade nothing else. " + \
                   "Return -2 if resume is irrelevant to the job description" + \
                   "Return -1 if job description is not understandable or if the resume data has nothing or not understandable or enough to make good judgement." + \
                   "If the max grade is 1, then 0 means the resume is not good enough and 1 means the resume is good enough. Also be harsh with your evaluations"

    messages = [{"role": "system", "content": systemString}]

    for resume in resumeList:
        individual_messages = messages.copy()  # Copy the base messages list
        individual_messages.append({"role": "user", "content": resume})

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=individual_messages
            )
            # Assuming each response contains a number directly (you may need to parse or process text)
            last_message = response.choices[0].message.content.strip()
            if int(last_message) == -1:
                grades.append("Error: ChatGPT could not grade the resume, based on the given data.")
            else:
                grades.append(last_message)
        except Exception as e:
            grades.append("Error: " + str(e))

    return grades

@app.post("/grade/ChatGPT/")
async def grade_chatgpt(requestData: GradeRequestData):
    """
    grades resumes using ChatGPT model.
    Args:
    - requestData (GradeRequestData): The request data containing the resume data and job description.

    Returns:
    - dict: A dictionary containing the grades for each resume and an error log.
    """
    grades: dict[int, int] = {}
    errorLog = {}
    ids = [*requestData.resumeData.keys()]
    resumeData = [*requestData.resumeData.values()]
    response = await _grade_resume_chatGPT(requestData.apiKey, requestData.jobDescription, resumeData, 1)
    for i in range(len(ids)):
        if "Error: " not in response[i]:
            grades[ids[i]] = int(response[i])
        else:
            errorLog[ids[i]] = response[i]
    return {"Grades" : grades, "errorLog": errorLog}


@app.post("/extract/Text/{filetype}")
def extractFromFile(filetype: str, file: UploadFile = File(...)):
    """
    Extracts resume data from a file.
    Args:
    - filetype (str): The type of the file, e.g., "pdf", "docx", etc.
    - file (UploadFile): The file to extract data from.

    Returns:
    - dict: A dictionary containing the extracted resume data.
    """
    extractedText = ""
    if filetype == "docx":
        extractedText = docx2txt.process(file.file)
    elif filetype == "pdf":
        extractedText = pypdf2.PdfReader(file.file).pages[0].extract_text()
    elif filetype == "txt":
        extractedText = file.file.read().decode("utf-8")
    return {"extractedText" : extractedText}


@app.post("/extract/resumeJSON/ChatGPT")
def extractResumeJSON(dataString: str, api_key: str):
    """
    Extracts resume data from a str and converts it to JSON format with ChatGPT.
    Args:
    - dataString (str): The resume data in string format.
    - api_key (str): The API key for authenticating with the OpenAI API.

    Returns:
    - dict: A dictionary containing the extracted resume data in JSON format.
    """
    client = OpenAI(api_key=api_key, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")

    systemString = "Use the given resume data to and convert it to json format. " + \
    "The format would be: {name: [firstName, lastName], phoneNo: '+XX-XXXXXXXXXX', email: email, " + \
    "experience: [\{'DDMMYYYY-DDMMYYYY': \{'COMPANY NAME': 'DESCRIPTION'\}\}, \{'DDMMYYYY-DDMMYYYY': \{'COMPANY NAME': 'DESCRIPTION'\}\}],"+\
    "skills: ['skill1', 'skill2'], education: [\{'DDMMYYYY-DDMMYYYY': \{'INSTITUTION': 'COURSE NAME'\}\}, ...]}  for dates if none given use 00000000" + \
    "the keys in the list should exactly be the same as in the format no matter what is being used in the resume data."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": systemString},
            {"role": "user", "content": dataString}
        ]
    )
    return response.choices[0].message.content
