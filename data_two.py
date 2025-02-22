import numpy as np
import pandas as pd

# Number of students
num_students = 500  

# Generate random data
np.random.seed(42)
grades = np.random.uniform(50, 100, num_students)  # Simulating midterm/final scores
submission_lateness = np.random.normal(0, 2, num_students)  # Mean on-time, some late
study_time = np.random.uniform(1, 20, num_students)  # Hours per week
course_difficulty = np.random.uniform(1, 10, num_students)  # Scale of 1-10

# Simulating failure probability based on weighted factors
failure_prob = 1 / (1 + np.exp(-(-0.05 * grades + 0.1 * submission_lateness - 0.05 * study_time + 0.2 * course_difficulty)))

# Convert to binary label (failed or not)
fail_label = (failure_prob > 0.5).astype(int)

# Create DataFrame
df = pd.DataFrame({
    "grades": grades,
    "submission_lateness": submission_lateness,
    "study_time": study_time,
    "course_difficulty": course_difficulty,
    "failure_prob": failure_prob,
    "fail_label": fail_label
})

print(df.head())
