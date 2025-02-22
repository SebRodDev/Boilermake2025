import re
import numpy as np
import pandas as pd
import random

# --- Syllabus Parsing Functions ---

def extract_course_name(text):
    """Extract course title from syllabus text."""
    match = re.search(r'Course Title:\s*(.*)', text)
    return match.group(1).strip() if match else "Unknown Course"

def extract_assignments_count(text):
    """Extract the number of assignments mentioned in the syllabus."""
    match = re.search(r'Assignments:.*?(\d+)', text, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def extract_exams_count(text):
    """Extract the number of exams mentioned in the syllabus."""
    match = re.search(r'Exams:.*?(\d+)', text, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def extract_grading_scheme(text):
    """
    Extract grading components and their weightage.
    Expected format in syllabus: "Grading Policy: Assignments: 40%, Exams: 50%, Projects: 10%"
    """
    grading = {}
    pattern = re.compile(r'(\w+):\s*(\d+)%')
    for component, percentage in pattern.findall(text):
        grading[component.lower()] = int(percentage)
    return grading

def parse_syllabus(syllabus_text):
    """Parse the syllabus text and return a dictionary of course properties."""
    course_name = extract_course_name(syllabus_text)
    assignments = extract_assignments_count(syllabus_text)
    exams = extract_exams_count(syllabus_text)
    grading_scheme = extract_grading_scheme(syllabus_text)
    return {
        'course_name': course_name,
        'assignments': assignments,
        'exams': exams,
        'grading_scheme': grading_scheme
    }

# --- Course Class ---

class Course:
    def __init__(self, syllabus_text):
        parsed = parse_syllabus(syllabus_text)
        self.name = parsed['course_name']
        self.num_assignments = parsed['assignments']
        self.num_exams = parsed['exams']
        self.grading_scheme = parsed['grading_scheme']
        
        # Ensure keys for our grading calculation exist (default to 0 if not provided)
        self.grading_scheme.setdefault('assignments', 0)
        self.grading_scheme.setdefault('exams', 0)
        self.grading_scheme.setdefault('projects', 0)
        
        # Normalize grading weights if they do not sum to 100
        total_weight = sum(self.grading_scheme.values())
        if total_weight != 100 and total_weight > 0:
            self.grading_scheme = {k: v / total_weight * 100 for k, v in self.grading_scheme.items()}
    
    def __repr__(self):
        return (f"Course(name={self.name}, num_assignments={self.num_assignments}, "
                f"num_exams={self.num_exams}, grading_scheme={self.grading_scheme})")

# --- Helper Function for Random Names ---

def generate_random_name():
    first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Ethan', 'Fiona', 'George', 'Hannah']
    last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# --- Student Data Generator ---

class StudentDataGenerator:
    def __init__(self, course, seed=42):
        """
        Initialize with a Course object.
        The course object contains syllabus-derived parameters (e.g., weightage, counts).
        """
        self.course = course
        np.random.seed(seed)
    
    def generate_student_data(self, num_students=100):
        data = []
        # Extract weights (convert percentages to fractions)
        assignment_weight = self.course.grading_scheme.get('assignments', 0) / 100.0
        exam_weight = self.course.grading_scheme.get('exams', 0) / 100.0
        project_weight = self.course.grading_scheme.get('projects', 0) / 100.0
        
        for i in range(num_students):
            student_id = f"{self.course.name.replace(' ', '_')}_{i}"
            name = generate_random_name()
            
            # --- Simulate Component Scores ---
            # For assignments: simulate multiple scores and take an average
            if self.course.num_assignments > 0:
                assignment_scores = np.clip(np.random.normal(75, 10, self.course.num_assignments), 0, 100)
                assignment_avg = np.mean(assignment_scores)
            else:
                assignment_avg = 0
            
            # For exams: simulate exam scores
            if self.course.num_exams > 0:
                exam_scores = np.clip(np.random.normal(70, 15, self.course.num_exams), 0, 100)
                exam_avg = np.mean(exam_scores)
            else:
                exam_avg = 0
                
            # For projects: if there is weight for projects, simulate a project score
            if project_weight > 0:
                project_score = np.clip(np.random.normal(80, 10), 0, 100)
            else:
                project_score = 0
            
            # --- Calculate Final Grade ---
            # Weighted sum of components as defined in the syllabus
            final_grade = (assignment_avg * assignment_weight +
                           exam_avg * exam_weight +
                           project_score * project_weight)
            
            # Assume current grade equals the computed final grade for simplicity
            current_grade = final_grade
            
            # --- Additional Metrics ---
            # Simulate other factors that might influence failure (attendance, study time, etc.)
            attendance_rate = np.clip(np.random.normal(0.85, 0.1), 0, 1)
            study_time = np.clip(np.random.normal(10, 3), 1, 30)
            submission_lateness = np.clip(np.random.normal(0, 1), -2, 5)
            
            # --- Failure Probability Calculation ---
            # A logistic model combining final grade and other factors.
            # Here, lower final grades, higher lateness, and lower attendance increase failure probability.
            failure_factor = (-0.05 * final_grade +
                              0.2 * submission_lateness -
                              0.1 * attendance_rate * 100 -
                              0.03 * study_time +
                              0.1 * (100 - final_grade))  # extra penalty for lower grades
            
            failure_prob = 1 / (1 + np.exp(-failure_factor))
            fail_label = 1 if failure_prob > 0.5 else 0
            
            # --- Append Student Record ---
            data.append({
                'student_id': student_id,
                'name': name,
                'assignment_avg': assignment_avg,
                'exam_avg': exam_avg,
                'project_score': project_score,
                'final_grade': final_grade,
                'current_grade': current_grade,  # Could be partial if desired
                'attendance_rate': attendance_rate,
                'study_time': study_time,
                'submission_lateness': submission_lateness,
                'failure_prob': failure_prob,
                'fail_label': fail_label
            })
        
        return pd.DataFrame(data)

# --- Example Usage ---

syllabus_text = """
Course Title: Introduction to Data Science
Assignments: There will be 5 assignments.
Exams: There will be 2 exams.
Grading Policy: Assignments: 40%, Exams: 50%, Projects: 10%
"""

# Create Course object by parsing the syllabus
course = Course(syllabus_text)
print(course)

# Generate synthetic student data for the course
generator = StudentDataGenerator(course)
student_data = generator.generate_student_data(num_students=50)
print(student_data.head())
