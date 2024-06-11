## Resume Grader API Endpoints

### Create a New User

**Endpoint**: `/users/`

**Method**: `POST`

**Description**: Create a new user.

**Example Request**:
    ```json
    {
        "uid": "user123",
        "name": "John Doe",
        "dob": "01011990",
        "is_owner": true,
        "is_admin": false,
        "phone_number": "91-9876543210",
        "email": "john.doe@example.com"
    }
    ```

**Example Response**:
    ```json
    {
        "message": "User created successfully."
    }
    ```

### Retrieve a User by UID

**Endpoint**: `/users/{uid}`

**Method**: `GET`

**Description**: Retrieve a user by UID.

**Example Request**:
    ```json
    {
        "uid": "user123"
    }
    ```

**Example Response**:
    ```json
    {
        "uid": "user123",
        "name": "John Doe",
        "dob": "01011990",
        "is_owner": true,
        "is_admin": false,
        "phone_number": "91-9876543210",
        "email": "john.doe@example.com"
    }
    ```

### Update an Existing User

**Endpoint**: `/users/`

**Method**: `PUT`

**Description**: Update an existing user.

**Example Request**:
    ```json
    {
        "uid": "user123",
        "name": "John Doe",
        "dob": "01011990",
        "is_owner": true,
        "is_admin": false,
        "phone_number": "91-9876543210",
        "email": "john.doe@example.com"
    }
    ```

**Example Response**:
    ```json
    {
        "message": "User updated successfully."
    }
    ```

### Delete a User by UID

**Endpoint**: `/users/{uid}`

**Method**: `DELETE`

**Description**: Delete a user by UID.

**Example Request**:
    ```json
    {
        "uid": "user123"
    }
    ```

**Example Response**:
    ```json
    {
        "message": "User deleted successfully."
    }
    ```

### Retrieve All Users

**Endpoint**: `/users/`

**Method**: `GET`

**Description**: Retrieve all users.

**Example Response**:
    ```json
    [
        {
            "uid": "user123",
            "name": "John Doe",
            "dob": "01011990",
            "is_owner": true,
            "is_admin": false,
            "phone_number": "91-9876543210",
            "email": "john.doe@example.com"
        },
        {
            "uid": "user456",
            "name": "Jane Smith",
            "dob": "02021985",
            "is_owner": false,
            "is_admin": true,
            "phone_number": "91-9876543211",
            "email": "jane.smith@example.com"
        }
    ]
    ```

### Create a New Resume

**Endpoint**: `/resumes/`

**Method**: `POST`

**Description**: Create a new resume.

**Example Request**:
    ```json
    {
        "uid": "user123",
        "skills": ["Python", "Java"],
        "experience": [
            {"start_date": "01012020", "end_date": "01012021", "title": "Developer", "company_name": "Company A", "description": "Worked on projects."}
        ],
        "education": [
            {"start_date": "01012015", "end_date": "01012019", "institution": "University A", "course_name": "Computer Science"}
        ]
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Resume created successfully."
    }
    ```

### Retrieve a Resume by User ID

**Endpoint**: `/resumes/{uid}`

**Method**: `GET`

**Description**: Retrieve a resume by user ID.

**Example Request**:
    ```json
    {
        "uid": "user123"
    }
    ```

**Example Response**:
    ```json
    {
        "uid": "user123",
        "skills": ["Python", "Java"],
        "experience": [
            {"start_date": "01012020", "end_date": "01012021", "title": "Developer", "company_name": "Company A", "description": "Worked on projects."}
        ],
        "education": [
            {"start_date": "01012015", "end_date": "01012019", "institution": "University A", "course_name": "Computer Science"}
        ]
    }
    ```

### Update an Existing Resume

**Endpoint**: `/resumes/`

**Method**: `PUT`

**Description**: Update an existing resume.

**Example Request**:
    ```json
    {
        "uid": "user123",
        "skills": ["Python", "Java"],
        "experience": [
            {"start_date": "01012020", "end_date": "01012021", "title": "Developer", "company_name": "Company A", "description": "Worked on projects."}
        ],
        "education": [
            {"start_date": "01012015", "end_date": "01012019", "institution": "University A", "course_name": "Computer Science"}
        ]
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Resume updated successfully."
    }
    ```

### Delete a Resume by User ID

**Endpoint**: `/resumes/{uid}`

**Method**: `DELETE`

**Description**: Delete a resume by user ID.

**Example Request**:
    ```json
    {
        "uid": "user123"
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Resume deleted successfully."
    }
    ```

### Retrieve All Resumes

**Endpoint**: `/resumes/`

**Method**: `GET`

**Description**: Retrieve all resumes.

**Example Response**:
    ```json
    [
        {
            "uid": "user123",
            "skills": ["Python", "Java"],
            "experience": [
                {"start_date": "01012020", "end_date": "01012021", "title": "Developer", "company_name": "Company A", "description": "Worked on projects."}
            ],
            "education": [
                {"start_date": "01012015", "end_date": "01012019", "institution": "University A", "course_name": "Computer Science"}
            ]
        },
        {
            "uid": "user456",
            "skills": ["C++", "Go"],
            "experience": [
                {"start_date": "01012018", "end_date": "01012019", "title": "Engineer", "company_name": "Company B", "description": "Worked on software development."}
            ],
            "education": [
                {"start_date": "01012014", "end_date": "01012018", "institution": "University B", "course_name": "Software Engineering"}
            ]
        }
    ]
    ```

### Create a New Job

**Endpoint**: `/jobs/`

**Method**: `POST`

**Description**: Create a new job.

**Example Request**:
    ```json
    {
        "job_id": 1,
        "title": "Software Engineer",
        "company": "TechCorp",
        "description": "Develop and maintain software applications.",
        "required_skills": ["Python", "Django"],
        "application_deadline": "01062024",
        "location": "Remote",
        "salary": 75000.00,
        "job_type": "FULL",
        "active": true
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Job created successfully."
    }
    ```

### Retrieve a Job by Job ID

**Endpoint**: `/jobs/{job_id}`

**Method**: `GET`

**Description**: Retrieve a job by job ID.

**Example Request**:
    ```json
    {
        "job_id": 1
    }
    ```

**Example Response**:
    ```json
    {
        "job_id": 1,
        "title": "Software Engineer",
        "company": "TechCorp",
        "description": "Develop and maintain software applications.",
        "required_skills": ["Python", "Django"],
        "application_deadline": "01062024",
        "location": "Remote",
        "salary": 75000.00,
        "job_type": "FULL",
        "active": true
    }
    ```

### Update an Existing Job

**Endpoint**: `/jobs/`

**Method**: `PUT`

**Description**: Update an existing job.

**Example Request**:
    ```json
    {
        "job_id": 1,
        "title": "Software Engineer",
        "company": "TechCorp",
        "description": "Develop and maintain software applications.",
        "required_skills": ["Python", "Django"],
        "application_deadline": "01062024",
        "location": "Remote",
        "salary": 75000.00,
        "job_type": "FULL",
        "active": true
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Job updated successfully."
    }
    ```

### Delete a Job by Job ID

**Endpoint**: `/jobs/{job_id}`

**Method**: `DELETE`

**Description**: Delete a job by job ID.

**Example Request**:
    ```json
    {
        "job_id": 1
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Job deleted successfully."
    }
    ```

### Retrieve All Jobs

**Endpoint**: `/jobs/`

**Method**: `GET`

**Description**: Retrieve all jobs.

**Example Response**:
    ```json
    [
        {
            "job_id": 1,
            "title": "Software Engineer",
            "company": "TechCorp",
            "description": "Develop and maintain software applications.",
            "required_skills": ["Python", "Django"],
            "application_deadline": "01062024",
            "location": "Remote",
            "salary": 75000.00,
            "job_type": "FULL",
            "active": true
        },
        {
            "job_id": 2,
            "title": "Data Scientist",
            "company": "DataCorp",
            "description": "Analyze data and build predictive models.",
            "required_skills": ["Python", "Machine Learning"],
            "application_deadline": "15072024",
            "location": "San Francisco",
            "salary": 95000.00,
            "job_type": "FULL",
            "active": true
        }
    ]
    ```

### Create a New Match (Job Application)

**Endpoint**: `/matches/`

**Method**: `POST`

**Description**: Create a new match (job application).

**Example Request**:
    ```json
    {
        "match_id": 1,
        "uid": "user123",
        "job_id": 1,
        "status": "Applied",
        "status_code": 100,
        "grade": 85.5,
        "selected_skills": ["Python", "Django"]
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Match created successfully."
    }
    ```

### Retrieve All Matches for a Specific User ID

**Endpoint**: `/matches/{uid}`

**Method**: `GET`

**Description**: Retrieve all matches (job applications) for a specific user ID.

**Example Request**:
    ```json
    {
        "uid": "user123"
    }
    ```

**Example Response**:
    ```json
    [
        {
            "match_id": 1,
            "uid": "user123",
            "job_id": 1,
            "status": "Applied",
            "status_code": 100,
            "grade": 85.5,
            "selected_skills": ["Python", "Django"]
        },
        {
            "match_id": 2,
            "uid": "user123",
            "job_id": 2,
            "status": "Interviewed",
            "status_code": 200,
            "grade": 90.0,
            "selected_skills": ["Machine Learning", "Data Analysis"]
        }
    ]
    ```

### Update an Existing Match

**Endpoint**: `/matches/`

**Method**: `PUT`

**Description**: Update an existing match.

**Example Request**:
    ```json
    {
        "match_id": 1,
        "uid": "user123",
        "job_id": 1,
        "status": "Applied",
        "status_code": 100,
        "grade": 85.5,
        "selected_skills": ["Python", "Django"]
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Match updated successfully."
    }
    ```

### Delete a Match by Match ID

**Endpoint**: `/matches/{match_id}`

**Method**: `DELETE`

**Description**: Delete a match by match ID.

**Example Request**:
    ```json
    {
        "match_id": 1
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Match deleted successfully."
    }
    ```

### Retrieve All Matches

**Endpoint**: `/matches/`

**Method**: `GET`

**Description**: Retrieve all matches (job applications).

**Example Response**:
    ```json
    [
        {
            "match_id": 1,
            "uid": "user123",
            "job_id": 1,
            "status": "Applied",
            "status_code": 100,
            "grade": 85.5,
            "selected_skills": ["Python", "Django"]
        },
        {
            "match_id": 2,
            "uid": "user456",
            "job_id": 2,
            "status": "Interviewed",
            "status_code": 200,
            "grade": 90.0,
            "selected_skills": ["Machine Learning", "Data Analysis"]
        }
    ]
    ```

### Create New Feedback

**Endpoint**: `/feedback/`

**Method**: `POST`

**Description**: Create new feedback.

**Example Request**:
    ```json
    {
        "feedback_id": 1,
        "match_id": 1,
        "feedback_text": "Great candidate with strong technical skills."
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Feedback created successfully."
    }
    ```

### Retrieve Feedback by Feedback ID

**Endpoint**: `/feedback/{feedback_id}`

**Method**: `GET`

**Description**: Retrieve feedback by feedback ID.

**Example Request**:
    ```json
    {
        "feedback_id": 1
    }
    ```

**Example Response**:
    ```json
    {
        "feedback_id": 1,
        "match_id": 1,
        "feedback_text": "Great candidate with strong technical skills."
    }
    ```

### Update Existing Feedback

**Endpoint**: `/feedback/`

**Method**: `PUT`

**Description**: Update existing feedback.

**Example Request**:
    ```json
    {
        "feedback_id": 1,
        "match_id": 1,
        "feedback_text": "Great candidate with strong technical skills."
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Feedback updated successfully."
    }
    ```

### Delete Feedback by Feedback ID

**Endpoint**: `/feedback/{feedback_id}`

**Method**: `DELETE`

**Description**: Delete feedback by feedback ID.

**Example Request**:
    ```json
    {
        "feedback_id": 1
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Feedback deleted successfully."
    }
    ```

### Retrieve All Feedback

**Endpoint**: `/feedback/`

**Method**: `GET`

**Description**: Retrieve all feedback.

**Example Response**:
    ```json
    [
        {
            "feedback_id": 1,
            "match_id": 1,
            "feedback_text": "Great candidate with strong technical skills."
        },
        {
            "feedback_id": 2,
            "match_id": 2,
            "feedback_text": "Needs improvement in communication skills."
        }
    ]
    ```

### Upload Resume and Extract Data

**Endpoint**: `/upload/resume`

**Method**: `POST`

**Description**: Upload a resume file and extract its data.

**Example Request**:
    ```json
    {
        "file": "resume.pdf",
        "uid": "user123"
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Resume uploaded and data extracted successfully.",
        "resume_data": {
            "uid": "user123",
            "skills": ["Python", "Java"],
            "experience": [
                {"start_date": "01012020", "end_date": "01012021", "title": "Developer", "company_name": "Company A", "description": "Worked on projects."}
            ],
            "education": [
                {"start_date": "01012015", "end_date": "01012019", "institution": "University A", "course_name": "Computer Science"}
            ]
        }
    }
    ```

### Upload Job Description and Extract Data

**Endpoint**: `/upload/jobdescription`

**Method**: `POST`

**Description**: Upload a job description file and extract its data.

**Example Request**:
    ```json
    {
        "file": "job_description.pdf"
    }
    ```

**Example Response**:
    ```json
    {
        "message": "Job description uploaded and data extracted successfully.",
        "job_data": {
            "title": "Software Engineer",
            "company": "TechCorp",
            "description": "Develop and maintain software applications.",
            "required_skills": ["Python", "Django"],
            "application_deadline": "01062024",
            "location": "Remote",
            "salary": 75000.00,
            "job_type": "FULL",
            "active": true
        }
    }
    ```

### Grade All Resumes for a Specific Job

**Endpoint**: `/grade/job/{job_id}`

**Method**: `POST`

**Description**: Grade all resumes for a specific job.

**Example Request**:
    ```json
    {
        "job_id": 1
    }
    ```

**Example Response**:
    ```json
    {
        "message": "All resumes for job graded successfully."
    }
    ```

### Download Logs

**Endpoint**: `/logs`

**Method**: `GET`

**Description**: Download the logs as a zip file.

**Example Response**:
    ```json
    {
        "file": "logs.zip"
    }
    ```

### Update User Privileges

**Endpoint**: `/admin/update-privileges`

**Method**: `POST`

**Description**: Update user privileges (admin or owner).

**Example Request**:
    ```json
    {
        "target_uid": "user123",
        "is_admin": true,
        "is_owner": false,
        "admin_uid": "admin456"
    }
    ```

**Example Response**:
    ```json
    {
        "message": "User privileges updated successfully."
    }
    ```

### Grade All Resumes Attached to a Job Description

**Endpoint**: `/grade/job`

**Method**: `POST`

**Tags**: Grading

**Description**: Grade all resumes attached to a job description.

**Example Request**:
    ```json
    {
        "job_id": 1
    }
    ```

**Example Response**:
    ```json
    [
        {
            "match_id": 1,
            "uid": "user123",
            "job_id": 1,
            "status": "graded",
            "status_code": 85,
            "grade": 85,
            "selected_skills": ["skill1", "skill2"]
        }
    ]
    ```

**Raises**:
- `HTTPException`: If an error occurs during the grading process.

### Download Logs

**Endpoint**: `/logs/download`

**Method**: `GET`

**Tags**: Logs

**Description**: Download logs.

**Example Response**:
    ```json
    {
        "file": "logs.zip"
    }
    ```

**Raises**:
- `HTTPException`: If an error occurs during log retrieval.

### Get Matches by User ID

**Endpoint**: `/matches/uid`

**Method**: `POST`

**Tags**: Matches

**Description**: Get matches by user ID.

**Example Request**:
    ```json
    {
        "uid": "user123"
    }
    ```

**Example Response**:
    ```json
    [
        {
            "match_id": 1,
            "uid": "user123",
            "job_id": 1,
            "status": "Application received",
            "status_code": 100,
            "grade": 85,
            "selected_skills": ["skill1", "skill2"]
        }
    ]
    ```

**Raises**:
- `HTTPException`: If an error occurs during the retrieval process.

### Retrieve a Resume by User ID

**Endpoint**: `/resumes/{uid}`

**Method**: `GET`

**Tags**: Resumes

**Description**: Retrieve a resume by user ID.

**Example Request**:
    ```json
    {
        "uid": "user123"
    }
    ```

**Example Response**:
    ```json
    {
        "uid": "user123",
        "skills": ["Python", "Java"],
        "experience": [
            {
                "start_date": "01012020",
                "end_date": "01012021",
                "title": "Developer",
                "company_name": "Company",
                "description": "Description"
            }
        ],
        "education": [
            {
                "start_date": "01012018",
                "end_date": "01012022",
                "institution": "University",
                "course_name": "CS"
            }
        ]
    }
    ```

**Raises**:
- `HTTPException`: If an error occurs during the retrieval process.
