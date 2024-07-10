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
- [Documentation Swagger UI Custom Dark](https://resumegraderapi.onrender.com/darkDocs)
- [Documentation Swagger UI](https://resumegraderapi.onrender.com/docs)
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
### 1. Complete Grading Service

**Objective**: Implement a complete grading service that grades multiple resumes simultaneously and streams data back to the client in real-time. This will enhance the user experience and reduce the time taken to grade multiple resumes.

### 2. Implement Database Sessions

**Objective**: Introduce database sessions to manage transactions and ensure data integrity. This will improve the reliability and consistency of the API's interactions with the database.

### 3. Data Validation and Error Handling

**Objective**: Enhance data validation and error handling mechanisms to provide more detailed feedback to users and improve the overall robustness of the API.
Also resort to defaults when data is missing.


### 4. Documentation

**Objective**: Expand the API documentation to include detailed examples, use cases, and best practices for integrating the API into various applications. This will help users leverage the full potential of the API.

### 5. Logger Create new logging mechanism and platform for real time data

**Objective**: Implement a comprehensive logging mechanism to track API usage, errors, and performance metrics. This will help in monitoring and optimizing the API's performance and reliability.

### 6. Develop Tests and CI/CD Pipeline

**Objective**: Create a suite of tests to validate the API's functionalities and implement a CI/CD pipeline for automated testing and deployment. This will ensure the stability and quality of the API across different environments.

### 7. Performance and Efficiency Enhancements

**Objective**: Optimize the performance of the "grade all resumes for a job" endpoint and implement real-time updates to the client.

### 8. TAGS model

**Objective**: Implement a TAGS model to grade resumes based on the skills required for a job. This will provide a more granular and accurate assessment of resume-job fit.

### 9. Create models for resume and job description parsing

**Objective**: Develop models for parsing resume and job description data to extract relevant information and improve the grading accuracy.

# Updates
- [Version 1.0.0](#version-100)
- [Version 2.0.0](#version-200)
- [version 2.5.0](#version-250)
- [version 3.0.0](#version-300)
- [version 4.0.0](#version-400)


# Version 4.0.0
### Introduction
Version 4.0.0 is a reliability focused update that aims to enhance the performance, security, and scalability of the Resume Grader API. This version introduces new features, optimizations, and improvements to ensure a robust and efficient API experience. Here's a detailed look at the changes and enhancements in this update. The second thing this version focuses on is its maintainability and scalability. The source code is now divided into different packages talking with each other and doing their own specific tasks. This makes the codebase more modular and easier to maintain.

### Key Updates

#### Dark Mode Documentation

**Custom Swagger UI**

- **Dark Mode**: Introduced a dark mode for Swagger UI to provide a more comfortable user experience for those who prefer dark-themed interfaces. This is accessible via the `/darkDocs` endpoint.

#### Creation of Service Classes

**Services for Reusable Operations**

- **Service Classes**: Created service classes to provide a consistent and reusable way to handle complex operations. This includes handling user management, resume processing, job management, and more. Service classes encapsulate business logic, making the codebase more modular and maintainable.

#### API Key Authentication

**Enhanced Security**

- **Authentication**: Implemented API key authentication for certain endpoints to ensure that only authorized users can access these resources. This includes the creation and update endpoints for jobs.

**Endpoints with Authentication**:
    - **POST** `/jobs/`: Create a new job (requires API key)
    - **PUT** `/jobs/`: Update a job (requires API key)

#### Enhanced Endpoint Functionality

**Flexible Query Parameters**

- **Get Jobs**: Added query parameters to the **GET** `/jobs/` endpoint to allow filtering based on variables like active status and required skills.
- **Get Matches**: Enhanced the **GET** `/matches/` endpoint to support filtering based on various criteria, improving the flexibility and usefulness of the match retrieval process.

**New Functionalities**

- **Saved Jobs**: Introduced functionality for users to save jobs they are interested in. This feature helps users keep track of job opportunities they find appealing.

#### Refactoring and Code Organization

**Modular Codebase**

- **Packages**: The source code is now organized into different packages, each handling specific functionalities such as database operations, API endpoints, and utility functions. This modular structure enhances maintainability and scalability.

    - ['Database'](https://github.com/SidhuHarijot/ResumeGraderAPI/tree/main/Database): Contains database connection and query functions.
    - ['ServerLogging'](https://github.com/SidhuHarijot/ResumeGraderAPI/tree/main/ServerLogging): Manages logging operations and log file handling.
    - ['Models'](https://github.com/SidhuHarijot/ResumeGraderAPI/tree/main/Models): Defines data models and Pydantic schemas for request and response objects.
    - ['Services'](https://github.com/SidhuHarijot/ResumeGraderAPI/tree/main/Services): Implements business logic and operations for grading, file handling, and data processing.
    - ['Utilities'](https://github.com/SidhuHarijot/ResumeGraderAPI/tree/main/Utilities): Contains utility functions for file operations, data validation, and API interactions.
    - ['Processing/Factories'](https://github.com/SidhuHarijot/ResumeGraderAPI/tree/main/Processing/Factories): Handles the creation of objects and data processing tasks.
    - ['Processing/DataValidation'](https://github.com/SidhuHarijot/ResumeGraderAPI/tree/main/Processing/DataValidation): Validates data integrity and formats for requests and responses.
    - ['static'](https://github.com/SidhuHarijot/ResumeGraderAPI/tree/main/static): Contains static files like custom css for the documentation.

#### Conclusion

Version 4.0.0 of the Resume Grader API represents a substantial upgrade, introducing new functionalities, improving existing features, and enhancing the overall structure and maintainability of the codebase. With modular code organization, enhanced documentation, robust logging, and efficient data handling, this version is well-equipped to meet the demands of modern recruitment processes.

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

