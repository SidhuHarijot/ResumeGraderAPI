from fastapi import FastAPI, File, UploadFile
from mangum import Mangum
from pydantic import BaseModel, model_validator
from openai import OpenAI
import PyPDF2 as pypdf2
import docx2txt
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

origins = [
    "http://localhost:3000",  # Adjust this to include the URL of your Next.js app
    "https://your-nextjs-deployment-url.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins, adjust for security in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


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


class ExtractRequestData(BaseModel):
    stringData: str
    apiKey: str

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
def extractResumeJSON(requestData: ExtractRequestData):
    """
    Extracts resume data from a str and converts it to JSON format with ChatGPT.
    Args:
    - dataString (str): The resume data in string format.
    - api_key (str): The API key for authenticating with the OpenAI API.

    Returns:
    - dict: A dictionary containing the extracted resume data in JSON format.
    """
    client = OpenAI(api_key=requestData.apiKey, organization="org-GOis1CERYv7FHaZeiFsY7VWA", project="proj_D4n3EBiP1DL9FWS2BkiuuGTa")

    systemString = "Use the given resume data to and convert it to json format. " + \
    "The format would be: {name: [firstName, lastName], phoneNo: '+XX-XXXXXXXXXX', email: email, " + \
    "experience: [\{'DDMMYYYY-DDMMYYYY': \{'COMPANY NAME': 'DESCRIPTION'\}\}, \{'DDMMYYYY-DDMMYYYY': \{'COMPANY NAME': 'DESCRIPTION'\}\}],"+\
    "skills: ['skill1', 'skill2'], education: [\{'DDMMYYYY-DDMMYYYY': \{'INSTITUTION': 'COURSE NAME'\}\}, ...]," + \
    "certificates: \{'institution name': 'certificate name'\}\}  for dates if none given use 00000000" + \
    "the keys in the list should exactly be the same as in the format no matter what is being used in the resume data." + \
    "You have to adhere strictly to the format given, you cant use July 2024 for dates convert it to like 00072024 " + \
    "Similarly for phone number just use hyper between the country code and the number. like +XX-XXXXXXXXXX so that the data is consistent. " 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": systemString},
            {"role": "user", "content": requestData.stringData}
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print(extractResumeJSON("Experience: Senior Software Developer, ABC Tech July 2020 - Present Led a team of developers in designing and implementing mobile applications using React Native; successfully reduced app load time by 30%. Developed dynamic, responsive web applications tailored for high traffic with React.js, enhancing user experience and interface accessibility. Collaborated closely with UX/UI designers and implemented CSS in JS to ensure applications are both functionally and aesthetically appealing. Skills: Languages: JavaScript (ES6+), TypeScript, HTML5, CSS3 Frameworks: React.js, React Native Tools: Git, Jenkins, Docker, AWS Education: B.S. in Computer Science, University of Tech, 2015-2019 Certifications: Certified React Developer, Tech Certification Institute, 2021", "sk-proj-rm22j6StTEDEZVhu3VtHT3BlbkFJYXBMtcQJ9RPE6jj9lI6T"))
