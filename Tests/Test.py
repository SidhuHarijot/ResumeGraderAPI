import requests
import tempfile
import os
import json

# Constants for API interaction
API_URL = "http://127.0.0.1:8000"
#API_KEY = os.environ["OPENAI_RESUMEGRADER_APIKEY"]

def upload_file(file_path, endpoint):
    """Uploads a file to the specified API endpoint and returns the response."""
    url = f"{API_URL}{endpoint}"
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        params = {'apiKey': API_KEY}
        response = requests.post(url, files=files, params=params)
    return response.json()

def grade_resume(job_id, resume_id):
    """Sends a request to grade the resume based on the job description."""
    url = f"{API_URL}/grade/ChatGPT/"
    data = {
        "job_id": job_id,
        "resume_id": resume_id,
        "apiKey": API_KEY,
        "maxGrade": 100  # You can adjust maxGrade as per your grading scale
    }
    response = requests.post(url, json=data)
    return response.json()

def main():
    # Take inputs
    while True:
        print("Enter resume data (type 'END' on a new line to finish):")
        resume_data_lines = []
        while True:
            line = input()
            if line == "END":
                break
            resume_data_lines.append(line)
        resume_data = "\n".join(resume_data_lines)
        
        print("Enter job description data (type 'END' on a new line to finish):")
        job_description_lines = []
        while True:
            line = input()
            if line == "END":
                break
            job_description_lines.append(line)
        job_description = "\n".join(job_description_lines)
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_resume:
            tmp_resume.write(resume_data.encode())
            resume_path = tmp_resume.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_job:
            tmp_job.write(job_description.encode())
            job_path = tmp_job.name

        # Upload files
        resume_response = upload_file(resume_path, "/upload/resume/")
        job_response = upload_file(job_path, "/upload/job/")
        
        # Get the IDs from responses
        resume_id = resume_response.get('resume_id')
        job_id = job_response.get('job_id')

        # Grade the resume
        grading_response = grade_resume(job_id, resume_id)
        print("Grading Response:", json.dumps(grading_response, indent=4))

        # Cleanup temporary files
        os.remove(resume_path)
        os.remove(job_path)

if __name__ == "__main__":
    dictionary = {"key": "value"}
    print(dictionary["not_key"]) 
