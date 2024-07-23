# Correct the list of grades and remove the ellipsis (...)
import matplotlib.pyplot as plt
import pandas as pd
from Database.MatchDatabase import MatchDatabase
from Database.database import Database

Database.initialize()
matches = MatchDatabase.get_all_matches()

grades = [match.grade for match in matches]

status_codes = [match.status_code for match in matches]

job_ids = [match.job_id for match in matches]

users = [match.uid[-4:] for match in matches]


# Sort the grades in increasing order
sorted_grades = sorted(grades)

sorted_status_codes = sorted(status_codes)

sorted_job_ids = sorted(job_ids)

sorted_users = sorted(users)

# Calculate the frequency of each grade
grade_counts = pd.Series(sorted_grades).value_counts().sort_index()

code_counts = pd.Series(sorted_status_codes).value_counts().sort_index()

job_counts = pd.Series(sorted_job_ids).value_counts().sort_index()

user_counts = pd.Series(sorted_users).value_counts().sort_index()

# Filter out grades that have a frequency of 0 (none in this case, but for clarity)
filtered_grade_counts = grade_counts[grade_counts > 0]
filtered_code_counts = code_counts[code_counts > 0]
filtered_job_counts = job_counts[job_counts > 0]
filtered_user_counts = user_counts[user_counts > 0]

# Plotting the frequency of grades
plt.figure(figsize=(10, 6))

# grades sub plot
plt.subplot(2, 2, 1)
filtered_grade_counts.plot(kind='bar', color='blue')
plt.title('Frequency of Grades')
plt.xlabel('Grade')
plt.ylabel('Frequency')

# status codes sub plot
plt.subplot(2, 2, 2)
filtered_code_counts.plot(kind='bar', color='orange')
plt.title('Frequency of Status Codes')
plt.xlabel('Status Code')
plt.ylabel('Frequency')

# job ids sub plot
plt.subplot(2, 2, 3)
filtered_job_counts.plot(kind='bar', color='green')
plt.title('Frequency of Job IDs')
plt.xlabel('Job ID')
plt.ylabel('Frequency')

# users sub plot
plt.subplot(2, 2, 4)
filtered_user_counts.plot(kind='bar', color='red')
plt.title('Frequency of Users')
plt.xlabel('User')
plt.ylabel('Frequency')

plt.tight_layout()

plt.show()

