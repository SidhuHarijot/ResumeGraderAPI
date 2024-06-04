# CRUD API Endpoints

## Endpoints

### Users
- **Create User**
  - **Endpoint**: `POST /users`
  - **Description**: Creates a new user.

- **Get User**
  - **Endpoint**: `GET /users/{user_id}`
  - **Description**: Retrieves a user by user_id.

- **Update User**
  - **Endpoint**: `PUT /users/{user_id}`
  - **Description**: Updates an existing user by user_id.

- **Delete User**
  - **Endpoint**: `DELETE /users/{user_id}`
  - **Description**: Deletes a user by user_id.

### Resumes
- **Create Resume**
  - **Endpoint**: `POST /resumes`
  - **Description**: Uploads a new resume.

- **Get Resume**
  - **Endpoint**: `GET /resumes/{resume_id}`
  - **Description**: Retrieves a resume by resume_id.

- **Update Resume**
  - **Endpoint**: `PUT /resumes/{resume_id}`
  - **Description**: Updates an existing resume by resume_id.

- **Delete Resume**
  - **Endpoint**: `DELETE /resumes/{resume_id}`
  - **Description**: Deletes a resume by resume_id.

### Job Descriptions
- **Create Job Description**
  - **Endpoint**: `POST /job-descriptions`
  - **Description**: Creates a new job description.

- **Get Job Description**
  - **Endpoint**: `GET /job-descriptions/{job_id}`
  - **Description**: Retrieves a job description by job_id.

- **Update Job Description**
  - **Endpoint**: `PUT /job-descriptions/{job_id}`
  - **Description**: Updates an existing job description by job_id.

- **Delete Job Description**
  - **Endpoint**: `DELETE /job-descriptions/{job_id}`
  - **Description**: Deletes a job description by job_id.

### Matches
- **Create Match**
  - **Endpoint**: `POST /matches`
  - **Description**: Creates a new match between a resume and a job description.

- **Get Match**
  - **Endpoint**: `GET /matches/{match_id}`
  - **Description**: Retrieves a match by match_id.

- **Update Match**
  - **Endpoint**: `PUT /matches/{match_id}`
  - **Description**: Updates an existing match by match_id.

- **Delete Match**
  - **Endpoint**: `DELETE /matches/{match_id}`
  - **Description**: Deletes a match by match_id.

### Feedback
- **Create Feedback**
  - **Endpoint**: `POST /feedback`
  - **Description**: Creates new feedback for a resume.

- **Get Feedback**
  - **Endpoint**: `GET /feedback/{feedback_id}`
  - **Description**: Retrieves feedback by feedback_id.

- **Update Feedback**
  - **Endpoint**: `PUT /feedback/{feedback_id}`
  - **Description**: Updates existing feedback by feedback_id.

- **Delete Feedback**
  - **Endpoint**: `DELETE /feedback/{feedback_id}`
  - **Description**: Deletes feedback by feedback_id.

### Additional Endpoints
- **Get Filtered Resumes**
  - **Endpoint**: `GET /resumes/filtered`
  - **Description**: Retrieves resumes filtered based on specified criteria (e.g., skills, location).

- **Grade Resume**
  - **Endpoint**: `POST /resumes/{resume_id}/grade`
  - **Description**: Grades a resume using the AI tool and stores the results.

- **Get Job Matches for Resume**
  - **Endpoint**: `GET /resumes/{resume_id}/matches`
  - **Description**: Retrieves job matches for a specific resume based on AI-generated matching criteria.

- **Get Resumes for Job Description**
  - **Endpoint**: `GET /job-descriptions/{job_id}/resumes`
  - **Description**: Retrieves resumes that match a specific job description.

- **Get User Feedback**
  - **Endpoint**: `GET /users/{user_id}/feedback`
  - **Description**: Retrieves feedback provided by a specific user.

- **Get Resume Feedback**
  - **Endpoint**: `GET /resumes/{resume_id}/feedback`
  - **Description**: Retrieves feedback for a specific resume.
