from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
import math

app = Flask(__name__)
CORS(app)  # Enable CORS

# Load the student grades data from the Parquet file
parquet_file_path = os.path.join(os.path.dirname(__file__), 'risks_week10.parquet')

if not os.path.exists(parquet_file_path):
    raise FileNotFoundError(f"Parquet file not found at: {parquet_file_path}")

try:
    student_grades_df = pd.read_parquet(parquet_file_path)
except Exception as e:
    raise RuntimeError(f"Error reading Parquet file: {e}")


# Convert DataFrame to list of dictionaries
student_grades = student_grades_df.to_dict(orient='records')

# Convert the list of dictionaries to a list of lists (array)

# Check for unique values in the 'week' column

# Filter rows where week is equal to 10
student_grades_df = student_grades_df[student_grades_df['week'] == 10]

# Add dynamic fields
def add_dynamic_fields(row):
    # Example logic to set dotColor based on failure probability
    if row['failure_prob'] is not None and row['failure_prob'] >= 0.65:
        row['dotColor'] = 'red'
    else:
        row['dotColor'] = 'green'
    
    if row['failure_prob'] is not None:
        row['failure_prob'] *= 100  # Convert failure probability to percentage
    # Example logic to set profilePicture (you can customize this)
    row['profilePicture'] = 'https://wallpapers.com/images/hd/generic-person-icon-profile-ulmsmhnz0kqafcqn-2.jpg'

    # Example logic to set name and subtext (you can customize this)
    row['name'] = f"Student {row['student_id']}"
    row['subtext'] = f"Course: {row['course_name']}, Week: {row['week']}"

    return row

student_grades_df = student_grades_df.apply(add_dynamic_fields, axis=1)

# Convert DataFrame to list of dictionaries
student_grades = student_grades_df.to_dict(orient='records')

@app.route('/api/student-grades', methods=['GET'])
def get_student_grades():
    return jsonify(student_grades)

if __name__ == '__main__':
    app.run(debug=True)