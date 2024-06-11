# Resume Grader API

## Tables of Contents
- [Introduction](#introduction)
- [Resources](#resources)
- [Key Functionalities](#key-functionalities)
- [Documentation](#documentation)
- [What's Next for this API](#whats-next-for-this-api)
- [Updates](#updates)


## Introduction
The Resume Grader API is an advanced, feature-rich platform designed to enhance the recruitment process through automation and intelligent data handling. This API offers a suite of tools to streamline the management of job applications and resumes, making it invaluable for HR professionals, recruitment agencies, and any organization involved in hiring.

## Resources
- [Endpoints](/Endpoints.md)
- [Documentation](https://resumegraderapi.onrender.com/docs)
- [Documentation Redoc](https://resumegraderapi.onrender.com/redoc)

### Key Functionalities

#### Comprehensive Resume and Job Management

Users can upload, retrieve, update, and manage detailed profiles of resumes and job descriptions. This functionality supports multiple file formats, including PDF and DOCX, ensuring adaptability and ease of integration with existing systems.

#### Automated Resume Grading

By integrating OpenAI's cutting-edge AI models, the API automates the grading of resumes against specified job descriptions. It offers detailed analysis and grading on a scale, providing both single and batch grading capabilities to cater to different organizational needs.

#### Robust Application Tracking

The API facilitates efficient tracking of job applications, maintaining detailed records of application statuses and timelines. This feature helps organizations monitor the progress of applications and make informed decisions throughout the recruitment process.

#### Secure and Efficient Database Interactions

Built on a reliable PostgreSQL framework with a connection pool for optimal performance, the API ensures quick data retrieval, updates, and secure transactions. This robust backend architecture supports high-load operations, making it scalable for expanding business needs.

#### Error Handling and Security Measures

With advanced error handling strategies and API key authentication, the API maintains high standards of reliability and security. This ensures that the data integrity and privacy of user data are upheld, minimizing risks and vulnerabilities.

#### Flexible CORS Configuration

The API is configured to support CORS, allowing it to accept requests from a predefined list of origins. This feature is crucial for seamless integration with diverse frontend platforms, enhancing the API's usability across different web and mobile applications.

#### Interactive API Documentation

FastAPI's automatic Swagger UI documentation provides interactive, real-time documentation. This not only helps in quick onboarding and testing but also serves as a constant, up-to-date reference for developers.

### Conclusion

The Resume Grader API is designed to be a dynamic, responsive tool that adapts to the evolving needs of the modern recruitment landscape. It offers both granular control over data management and high-level analytics, providing users with the insights needed to optimize their recruitment processes effectively.

## Documentation
**COMPLETE DOCS FOR THE API CAN BE FOUND [HERE](https://resumegraderapi.onrender.com/docs).**

# What's Next for this API

### 1. Authorization Checks

**Objective**: Ensure that only authorized users can make changes to data within the API.

**Steps**:

- **User Roles and Permissions**: Define user roles (e.g., admin, user, owner) and their respective permissions.
- **Middleware for UID Verification**: Implement middleware functions to check UID (user identification) against these roles and permissions for each endpoint. For example, only admins or owners should be able to update job descriptions or grade resumes.
- **Endpoint Security**: Update all endpoints to include UID verification. This involves checking the UID provided in the request against the database to confirm the user's role and permissions before allowing the operation.

**Example**:

    ```python
    def check_permission(uid: str, required_role: str):
        con = connection_pool.getconn()
        try:
            with con.cursor() as cursor:
                cursor.execute("SELECT role FROM Users WHERE uid = %s", (uid,))
                user_role = cursor.fetchone()[0]
                if user_role != required_role:
                    raise HTTPException(status_code=403, detail="Permission denied.")
        finally:
            connection_pool.putconn(con)

    @app.put("/update/job/{job_id}")
    async def update_job(job_id: int, job_data: dict, uid: str):
        check_permission(uid, "admin")
        # Proceed with updating the job
    ```

### 2. In-House Data Models

**Objective**: Develop custom models for resume data extraction and grading to improve control, accuracy, and reduce reliance on third-party services.

**Steps**:

- **Resume Data Extraction Model**:
    - **Data Collection**: Gather a diverse set of resumes to train and validate the model.
    - **Model Development**: Use NLP techniques and libraries (such as spaCy, NLTK, or custom deep learning models) to build a parser that can accurately extract relevant information (e.g., name, contact details, skills, experience) from resume text.
    - **Testing and Validation**: Thoroughly test the model on various resume formats to ensure robustness and accuracy.
- **Resume Grading Model**:
    - **Criteria Definition**: Define the criteria for grading resumes (e.g., relevance to job description, skills match, experience level).
    - **Model Training**: Train a machine learning model (using algorithms like decision trees, random forests, or neural networks) to evaluate resumes based on these criteria.
    - **Continuous Improvement**: Implement feedback loops to continuously improve the model based on user inputs and grading outcomes.

**Example**:

    ```python
    def extract_resume_data(resume_text: str) -> dict:
        # Placeholder function for in-house resume data extraction model
        extracted_data = {
            "name": ["John", "Doe"],
            "phoneNo": "+XX-XXXXXXXXXX",
            "email": "john.doe@example.com",
            "experience": [{"01012020-01012021": {"Company A": "Job Description"}}],
            "skills": ["Python", "Data Analysis"],
            "education": [{"01012015-01012019": {"University A": "Degree"}}],
            "certificates": {"Institution A": "Certificate"}
        }
        return extracted_data

    @app.post("/extract/resumeJSON/inhouse")
    async def extract_resume_json(requestData: ExtractRequestData):
        extracted_data = extract_resume_data(requestData.stringData)
        return extracted_data
    ```

### 3. Performance Enhancements

**Objective**: Optimize the performance of the "grade all resumes for a job" endpoint and implement real-time updates to the client.

**Steps**:

- **Parallel Processing**: Use asynchronous programming and parallel processing to grade multiple resumes simultaneously, reducing the overall processing time.
- **Batch Updates**: Update the database in batches to minimize the number of transactions and improve performance.
- **Real-Time Updates**: Implement WebSocket or similar technology to push updates to the client application in real-time as each resume is graded.

**Example**:

    ```python
    @app.post("/grade/ChatGPT/job/{job_id}")
    async def grade_all_from_job(request: GradingRequest):
        import asyncio

        async def grade_resume(resume_id):
            grade = await _grade_resume_chatGPT(request.apiKey, request.job_id, [resume_id], request.maxGrade)
            grade = grade[resume_id]
            await save_grade(resume_id, request.job_id, grade)
            # Push real-time update to client
            await websocket_manager.send_update(request.client_id, grade)
            return grade

        con = connection_pool.getconn()
        try:
            with con.cursor() as cursor:
                cursor.execute("SELECT resume_id FROM matches WHERE job_id = %s", (request.job_id,))
                resume_ids = cursor.fetchall()
        finally:
            connection_pool.putconn(con)

        tasks = [grade_resume(resume_id[0]) for resume_id in resume_ids]
        grades = await asyncio.gather(*tasks)
        return {"status": "Success", "grades": grades}
    ```

### 4. Additional Improvements

**Objective**: Enhance the overall functionality, maintainability, and user experience of the API.

**Steps**:

- **Continuous Integration and Deployment (CI/CD)**:
    - Set up CI/CD pipelines using tools like GitHub Actions, Travis CI, or Jenkins to automate testing and deployment processes. This ensures that any changes are thoroughly tested and deployed efficiently.
- **Logging and Monitoring**:
    - Implement comprehensive logging using libraries like loguru or logging to track API requests, responses, and errors.
    - Set up monitoring tools like Prometheus and Grafana to keep track of the API's performance and health.
- **Documentation Updates**:
    - Update the API documentation to reflect new features and changes. Use tools like Swagger or Redoc to generate interactive API documentation.
    - Provide detailed guides and examples to help users understand how to use the new features.

**Example CI/CD Pipeline (GitHub Actions)**:

    ```yaml
    name: CI/CD Pipeline

    on:
      push:
        branches:
          - main
      pull_request:
        branches:
          - main

    jobs:
      build:
        runs-on: ubuntu-latest

        steps:
        - name: Checkout code
          uses: actions/checkout@v2

        - name: Set up Python
          uses: actions/setup-python@v2
          with:
            python-version: '3.8'

        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt

        - name: Run tests
          run: |
            pytest

        - name: Deploy to Production
          if: github.ref == 'refs/heads/main'
          run: |
            # Add deployment commands here
    ```

By focusing on these detailed improvements, the API will become more secure, efficient, and user-friendly, while also being easier to maintain and scale.



# Updates
- [Version 1.0.0](#version-100)
- [Version 2.0.0](#version-200)
- [version 2.5.0](#version-250)
- [version 3.0.0](#version-300)

# Version 3.0.0
### Introduction

Version 3.0.0 of the Resume Grader API brings significant enhancements, refactoring, and new functionalities. This update focuses on improving the robustness, maintainability, and security of the API. It introduces static utility classes, comprehensive validation, new request models, and improved logging mechanisms. Here's a detailed look at the changes and improvements.

### Key Updates

#### 1. Refactoring and Code Organization

**Static Utility Classes**

- **OpenAI Utility**: This class handles interactions with OpenAI's API for tasks such as grading resumes and extracting structured data from resume texts. The class is designed to be reusable and easily configurable.
- **File Utility**: A static class for managing file operations, including saving temporary files and extracting text from PDF, DOCX, and TXT files. This utility ensures efficient file handling and text extraction.

**Services for Complex Tasks**

Introduced service classes to handle complex operations, such as grading multiple resumes and processing file uploads. These services encapsulate business logic, making the codebase more modular and maintainable.

#### 2. New Endpoints and Functionalities

**File Upload and Processing**

- `/upload/resume`: Endpoint to upload a resume file (PDF, DOCX, TXT) or a long string. Uses OpenAI to convert the resume content into a structured JSON format.
- `/upload/job_description`: Similar to the resume upload, this endpoint handles job description files and extracts structured data using OpenAI.

**Resume and Job Description Extraction**

- `/extract/resume`: Converts uploaded resume files into a structured JSON format.
- `/extract/job_description`: Converts uploaded job description files into a structured JSON format.

**Grading**

- `/grade/job/{job_id}`: Grades all resumes attached to a specific job using OpenAI's grading capabilities. This endpoint processes resumes in parallel to optimize performance.

**Match Retrieval**

- `/matches/{uid}`: Retrieves all matches (job applications) associated with a specific user ID. This endpoint ensures that users can track their application statuses efficiently.

#### 3. Data Models and Validation

**Comprehensive Data Models**

- **User, Resume, Job, Match, Feedback**: Detailed data models using Pydantic to ensure data integrity and validation.
- **Request Models**: Separate request models for operations that require additional authentication or validation, such as updating user privileges.

**Validation**

- **Validation Class**: Static methods to validate email, phone numbers, dates, and the integrity of User, Resume, Job, Match, and Feedback objects. Ensures that all data entering the system adheres to expected formats and constraints.

#### 4. Logging and Error Handling

**Logging**

- **Logger Class**: Centralized logging for different parts of the application (factories, database, validation, services). Ensures consistent and detailed logging across the API.
- **Log File Management**: Endpoints to compress and decompress log files for efficient storage and retrieval. This includes:
    - `/logs/compress`: Compresses and downloads logs.
    - `/logs/decompress`: Decompresses and downloads logs.

#### 5. Database and Table Structures

**Updated Table Structures**

- **Users Table**: Enhanced to include detailed user information and roles.
- **Resumes Table**: Stores structured resume data, including skills, experience, and education in JSONB format.
- **JobDescriptions Table**: Stores job details with structured required skills and application deadlines.
- **Matches Table**: Tracks job applications and their statuses.
- **Feedback Table**: Stores feedback on job applications.

#### 6. Removed Endpoints

Certain endpoints that were deemed redundant or unnecessary were removed to streamline the API. These changes ensure that the API remains efficient and maintainable.

### Conclusion

Version 3.0.0 of the Resume Grader API represents a substantial upgrade, introducing new functionalities, improving existing features, and enhancing the overall structure and maintainability of the codebase. With static utility classes, comprehensive validation, robust logging, and efficient data handling, this version is well-equipped to meet the demands of modern recruitment processes.

# Version 2.5.0

### Changes in the Table Structures

#### Updated Table Structures

##### Users Table

    ```sql
    CREATE TABLE Users (
        user_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        dob DATE,
        uid VARCHAR(50) NOT NULL,
        is_owner BOOLEAN DEFAULT FALSE,
        is_admin BOOLEAN DEFAULT FALSE,
        phone_number VARCHAR(10),
        email VARCHAR(100) NOT NULL UNIQUE
    );
    ```

##### Resumes Table

    ```sql
    CREATE TABLE Resumes (
        resume_id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        skills VARCHAR(100)[],
        experience VARCHAR(1000)[],
        education VARCHAR(1000)[],
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    );
    ```

##### JobDescriptions Table

    ```sql
    CREATE TABLE JobDescriptions (
        job_id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        company VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        required_skills TEXT,
        application_deadline DATE,
        location VARCHAR(100),
        salary DECIMAL(10, 2),
        highly_preferred_skills VARCHAR(100)[],
        low_preferred_skills VARCHAR(100)[],
        rating DECIMAL(5, 2)
    );
    ```

##### Matches Table

    ```sql
    CREATE TABLE Matches (
        match_id SERIAL PRIMARY KEY,
        resume_id INT NOT NULL,
        job_id INT NOT NULL,
        match_percentage DECIMAL(5, 2),
        status VARCHAR(100),
        status_code INT,
        grade INT,
        highly_preferred_skills VARCHAR(100)[],
        low_preferred_skills VARCHAR(100)[],
        FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id),
        FOREIGN KEY (job_id) REFERENCES JobDescriptions(job_id)
    );
    ```

##### Feedback Table

    ```sql
    CREATE TABLE Feedback (
        feedback_id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        resume_id INT NOT NULL,
        feedback_text TEXT NOT NULL,
        rating INT CHECK (rating >= 1 AND rating <= 5),
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id)
    );
    ```

### Updated Functions and Endpoints

#### Table Creation

- Updated the `createTables` function to drop old tables and create new tables according to the new structure.

#### Endpoint Updates

- `/upload/application`: Updated to reflect the changes in the `Matches` table.
- `/retrieve/resume/{resume_id}`: Updated to query the `Resumes` table.
- `/retrieve/job/{job_id}`: Updated to query the `JobDescriptions` table.
- `/retrieve/match/{match_id}`: Updated to query the `Matches` table.
- `/retrieve/resumes/`: Updated to query the `Resumes` table.
- `/retrieve/jobs/`: Updated to query the `JobDescriptions` table.
- `/retrieve/grades/`: Updated to query the `grades` table.
- `/retrieve/resumes_with_grades/`: Updated to join the `Resumes` and `grades` tables.
- `/update/job/{job_id}`: Updated to reflect changes in the `JobDescriptions` table.
- `/update/resume/{resume_id}`: Updated to reflect changes in the `Resumes` table.

#### Added Endpoints

- `/upload/user`: Endpoint for registering a new user.
- `/retrieve/profile/{uid}`: Endpoint for retrieving a user's profile, including user and resume data.
- `/update/profile/{uid}`: Endpoint for updating a user's profile, including user and resume data.
- `/extract/resume`: Endpoint for uploading a resume file and extracting data.


# Version 2.0.0
## Changes in the Table Structures

### Old Table Structures

#### Resume Table

    ```sql
     "resume": """
         resume_id SERIAL PRIMARY KEY,
         resume_data JSON
     """
    ```

#### Jobs Table

    ```sql
     "jobs": """
         job_id SERIAL PRIMARY KEY,
         job_data JSON,
         active BOOLEAN DEFAULT TRUE
     """
    ```

#### Grades Table

    ```sql
     "grades": """
         resume_id INT,
         job_id INT,
         grade INT,
         PRIMARY KEY (resume_id, job_id),
         FOREIGN KEY (resume_id) REFERENCES resume(resume_id),
         FOREIGN KEY (job_id) REFERENCES jobs(job_id)
     """
    ```

#### Applications Table

    ```sql
     "applications": """
         application_id SERIAL PRIMARY KEY,
         resume_id INT,
         job_id INT,
         application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         status TEXT,
         statusCode INT,
         FOREIGN KEY (resume_id) REFERENCES resume(resume_id),
         FOREIGN KEY (job_id) REFERENCES jobs(job_id)
     """
    ```

### New Table Structures

#### Users Table

    ```sql
     "Users": """
         CREATE TABLE Users (
             user_id SERIAL PRIMARY KEY,
             uid VARCHAR(50) NOT NULL,
             is_owner BOOLEAN DEFAULT FALSE,
             username VARCHAR(50) NOT NULL,
             email VARCHAR(100) NOT NULL UNIQUE,
             password_hash VARCHAR(100) NOT NULL,
             is_admin BOOLEAN DEFAULT FALSE, 
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
         );
     ```
    ```

#### Resumes Table

    ```sql
     "Resumes": """
         CREATE TABLE Resumes (
             resume_id SERIAL PRIMARY KEY,
             user_id INT NOT NULL,
             resume_file VARCHAR(2000) NOT NULL,
             upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             FOREIGN KEY (user_id) REFERENCES Users(user_id)
         );
     ```
    ```

#### JobDescriptions Table

    ```sql
     "JobDescriptions": """
         CREATE TABLE JobDescriptions (
             job_id SERIAL PRIMARY KEY,
             title VARCHAR(100) NOT NULL,
             company VARCHAR(100) NOT NULL,
             description TEXT NOT NULL,
             required_skills TEXT,
             application_deadline DATE,
             location VARCHAR(100),
             salary DECIMAL(10, 2),
             highly_preferred_skills VARCHAR(100)[],
             low_preferred_skills VARCHAR(100)[],
             rating DECIMAL(5, 2),
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
         );
     ```
    ```

#### Matches Table

    ```sql
     "Matches": """
         CREATE TABLE Matches (
             match_id SERIAL PRIMARY KEY,
             resume_id INT NOT NULL,
             job_id INT NOT NULL,
             match_percentage DECIMAL(5, 2),
             highly_preferred_skills VARCHAR(100)[],
             low_preferred_skills VARCHAR(100)[],
             rating DECIMAL(5, 2),
             FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id),
             FOREIGN KEY (job_id) REFERENCES JobDescriptions(job_id)
         );
     ```
    ```

#### Feedback Table

    ```sql
     "Feedback": """
         CREATE TABLE Feedback (
             feedback_id SERIAL PRIMARY KEY,
             user_id INT NOT NULL,
             resume_id INT NOT NULL,
             feedback_text TEXT NOT NULL,
             rating INT CHECK (rating >= 1 AND rating <= 5),
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             FOREIGN KEY (user_id) REFERENCES Users(user_id),
             FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id)
         );
     ```
    ```

## Updated Functions and Endpoints

### Table Creation

- Updated the `createTables` function to drop old tables and create new tables according to the new structure.

### Endpoint Updates

- `/upload/application`: Updated to reflect the changes in the `Matches` table.
- `/retrieve/resume/{resume_id}`: Updated to query the `Resumes` table.
- `/retrieve/job/{job_id}`: Updated to query the `JobDescriptions` table.
- `/retrieve/match/{match_id}`: Updated to query the `Matches` table.
- `/retrieve/resumes/`: Updated to query the `Resumes` table.
- `/retrieve/jobs/`: Updated to query the `JobDescriptions` table.
- `/retrieve/grades/`: Updated to query the `grades` table.
- `/retrieve/resumes_with_grades/`: Updated to join the `Resumes` and `grades` tables.
- `/update/job/{job_id}`: Updated to reflect changes in the `JobDescriptions` table.
- `/update/resume/{resume_id}`: Updated to reflect changes in the `Resumes` table.


# Version 1.0.0
  - Initial release of the Resume Grader API.

