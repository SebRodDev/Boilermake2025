import re
import numpy as np
import pandas as pd
import random
import PyPDF2
from math import exp

# --- Part 1: Syllabus Parsing from a PDF ---

def read_syllabus_pdf(file_path):
    """
    Reads a PDF file and extracts the text.
    Requires PyPDF2.
    """
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Functions to extract key properties from the syllabus text.
def extract_course_name(text):
    """Extract the course title from the syllabus."""
    match = re.search(r'Course Title:\s*(.*)', text, re.IGNORECASE)
    return match.group(1).strip() if match else "Unknown Course"

def extract_assignments_count(text):
    """
    Extracts the number of assignments mentioned.
    Expected pattern: "Assignments: ... <number>".
    """
    match = re.search(r'Assignments?:.*?(\d+)', text, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def extract_grading_scheme(text):
    """
    Extracts grading components and their weightage.
    Expected format: "Grading Policy: Assignments: 40%, Exams: 50%, Projects: 10%"
    """
    grading = {}
    pattern = re.compile(r'(\w+):\s*(\d+)%')
    for component, percentage in pattern.findall(text):
        grading[component.lower()] = int(percentage)
    return grading

def parse_syllabus(syllabus_text):
    """
    Parse the syllabus text and return a dictionary of course properties.
    For now, we extract the course title, number of assignments, and grading scheme.
    """
    course_name = extract_course_name(syllabus_text)
    assignments = extract_assignments_count(syllabus_text)
    grading_scheme = extract_grading_scheme(syllabus_text)
    return {
        'course_name': course_name,
        'assignments': assignments,
        'grading_scheme': grading_scheme
    }

# --- Course Object ---

class Course:
    def __init__(self, syllabus_text):
        parsed = parse_syllabus(syllabus_text)
        self.name = parsed['course_name']
        self.num_assignments = parsed['assignments']
        self.grading_scheme = parsed['grading_scheme']
        
        # Ensure that the grading scheme has an "assignments" key
        self.grading_scheme.setdefault('assignments', 0)
        # Normalize grading weights if they do not sum to 100 (if needed)
        total_weight = sum(self.grading_scheme.values())
        if total_weight != 100 and total_weight > 0:
            self.grading_scheme = {k: v / total_weight * 100 for k, v in self.grading_scheme.items()}
    
    def __repr__(self):
        return (f"Course(name={self.name}, num_assignments={self.num_assignments}, "
                f"grading_scheme={self.grading_scheme})")

# --- Helper for Generating Random Student Names ---

def generate_random_name():
    first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Ethan', 'Fiona', 'George', 'Hannah']
    last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# --- Part 2: Synthetic Student Data Generation over 10 Weeks ---

class StudentDataGenerator:
    def __init__(self, course, weeks=10, seed=42):
        """
        Initialize with a Course object and the number of weeks (default is 10).
        """
        self.course = course
        self.weeks = weeks
        np.random.seed(seed)
    
    def generate_student_data(self, num_students=100):
        """
        For each student, simulate weekly assignment grades and submission lateness.
        Then calculate:
          - cumulative_grade: the average grade over the 10-week period.
          - avg_lateness: the average submission lateness (normalized, e.g., 0: on time, 1: very late).
          - failure_prob: computed via a logistic function that combines grade and lateness.
          
        Returns a DataFrame of synthetic student records.
        """
        data = []
        # Parameters for synthetic data simulation (these can be tuned)
        grade_mean = 75
        grade_std = 10
        lateness_mean = 0.3   # average lateness score (0 to 1 scale)
        lateness_std = 0.2
        
        for i in range(num_students):
            student_id = f"{self.course.name.replace(' ', '_')}_{i}"
            name = generate_random_name()
            
            # Simulate 10 weekly assignment grades (each out of 100)
            weekly_grades = np.clip(np.random.normal(grade_mean, grade_std, self.weeks), 0, 100)
            cumulative_grade = np.mean(weekly_grades)
            
            # Simulate submission lateness for each week (normalized between 0 and 1)
            weekly_lateness = np.clip(np.random.normal(lateness_mean, lateness_std, self.weeks), 0, 1)
            avg_lateness = np.mean(weekly_lateness)
            
            # For demonstration, let’s also assume the syllabus grading scheme influences
            # the overall grade. For example, if assignments are weighted at X%, we might use that
            # weight to adjust the expected performance. Here we simply note the weight.
            assignment_weight = self.course.grading_scheme.get('assignments', 0) / 100.0
            
            # --- Calculate Failure Probability ---
            # A sample logistic function that uses cumulative_grade and avg_lateness.
            # The idea is: lower grades and higher lateness increase failure risk.
            # Here, we define:
            #    failure_factor = 0.05*(70 - cumulative_grade) + 0.2*(avg_lateness)
            # so that a student scoring below 70 with high lateness sees a higher failure probability.
            failure_factor = 0.05 * (70 - cumulative_grade) + 0.2 * (avg_lateness)
            failure_prob = 1 / (1 + exp(-failure_factor))
            
            # Append the student's record
            data.append({
                'student_id': student_id,
                'name': name,
                'cumulative_grade': cumulative_grade,
                'avg_lateness': avg_lateness,
                'failure_prob': failure_prob
            })
        
        df = pd.DataFrame(data)
        # Calculate and print class average for reference
        class_avg = df['cumulative_grade'].mean()
        print(f"Class Average Grade (after 10 weeks): {class_avg:.2f}")
        return df

# --- Example Usage ---

# If you have a syllabus PDF, specify the file path:
# syllabus_text = read_syllabus_pdf("syllabus.pdf")

# For demonstration purposes, we simulate a syllabus text:
syllabus_text = """
Course Title: Introduction to Data Science
Assignments: There will be 10 assignments.
Grading Policy: Assignments: 40%, Exams: 50%, Projects: 10%
"""

# Parse the syllabus and create a Course object
course = Course(syllabus_text)
print("Parsed Course Information:")
print(course)

# Generate synthetic student data for a 10-week period based on the course syllabus
generator = StudentDataGenerator(course, weeks=10)
student_data = generator.generate_student_data(num_students=50)

print("\nSample Synthetic Student Data:")
print(student_data.head())
