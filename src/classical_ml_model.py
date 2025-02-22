import re
import numpy as np
import pandas as pd
import random
from math import exp
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# === Syllabus Parsing Functions ===

def extract_course_name(text):
    """Extracts the course title from the syllabus text."""
    match = re.search(r'Course Title:\s*(.*)', text, re.IGNORECASE)
    return match.group(1).strip() if match else "Unknown Course"

def extract_grading_scheme(text):
    """
    Extracts grading components and their weightage.
    Expected format in the syllabus:
      "Grading Policy: Homeworks: 40%, Quizzes: 20%, Exams: 40%"
    """
    grading = {}
    pattern = re.compile(r'(\w+):\s*(\d+)%')
    for component, percentage in pattern.findall(text):
        grading[component.lower()] = int(percentage)
    return grading

def extract_passing_grade(text):
    """
    Extracts the passing grade from the syllabus text.
    Expected format: "Passing Grade: 60"
    """
    match = re.search(r'Passing Grade:\s*(\d+)', text, re.IGNORECASE)
    return float(match.group(1)) if match else 60.0

def parse_syllabus(syllabus_text):
    """Parses the syllabus text and returns course properties."""
    course_name = extract_course_name(syllabus_text)
    grading_scheme = extract_grading_scheme(syllabus_text)
    passing_grade = extract_passing_grade(syllabus_text)
    return {
        'course_name': course_name,
        'grading_scheme': grading_scheme,
        'passing_grade': passing_grade
    }

# === Course Object ===

class Course:
    def __init__(self, syllabus_text):
        parsed = parse_syllabus(syllabus_text)
        self.name = parsed['course_name']
        self.grading_scheme = parsed['grading_scheme']
        self.passing_grade = parsed['passing_grade']
        # Ensure required components exist: homeworks, quizzes, exams.
        for comp in ['homeworks', 'quizzes', 'exams']:
            self.grading_scheme.setdefault(comp, 0)
        # Normalize weights to sum to 100 (if needed).
        total_weight = sum(self.grading_scheme.values())
        if total_weight != 100 and total_weight > 0:
            self.grading_scheme = {k: (v / total_weight * 100) for k, v in self.grading_scheme.items()}
    
    def __repr__(self):
        return (f"Course(name={self.name}, grading_scheme={self.grading_scheme}, "
                f"passing_grade={self.passing_grade})")

# === Helper Function: Generate Random Student Name ===

def generate_random_name():
    first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Ethan', 'Fiona', 'George', 'Hannah']
    last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# === Synthetic Student Data Generation (10-Week Period) ===

class StudentDataGenerator:
    def __init__(self, course, weeks=10, seed=42):
        self.course = course
        self.weeks = weeks
        np.random.seed(seed)
    
    def generate_student_data(self, num_students=100):
        """
        For each student:
          - Generate weekly homework and quiz scores over 10 weeks.
          - Generate one exam score.
          - Compute the average scores and final grade (weighted sum).
          - Label fail if the final grade is below the passing grade.
          - Log which component(s) are below the passing threshold.
        Returns a DataFrame of student records.
        """
        data = []
        for i in range(num_students):
            student_id = f"{self.course.name.replace(' ', '_')}_{i}"
            name = generate_random_name()
            
            # Generate synthetic grades (each out of 100)
            homeworks = np.clip(np.random.normal(75, 10, self.weeks), 0, 100)
            quizzes = np.clip(np.random.normal(70, 15, self.weeks), 0, 100)
            exam = np.clip(np.random.normal(65, 20, 1), 0, 100)[0]
            
            homework_avg = np.mean(homeworks)
            quiz_avg = np.mean(quizzes)
            
            # Retrieve weights from the course's grading scheme
            weight_hw = self.course.grading_scheme.get('homeworks', 0) / 100.0
            weight_quiz = self.course.grading_scheme.get('quizzes', 0) / 100.0
            weight_exam = self.course.grading_scheme.get('exams', 0) / 100.0
            
            final_grade = homework_avg * weight_hw + quiz_avg * weight_quiz + exam * weight_exam
            
            # Label failure based on the predefined passing grade
            fail_label = 1 if final_grade < self.course.passing_grade else 0
            
            # Log which component(s) the student is struggling on (score below passing grade)
            struggle_components = []
            if homework_avg < self.course.passing_grade:
                struggle_components.append("homeworks")
            if quiz_avg < self.course.passing_grade:
                struggle_components.append("quizzes")
            if exam < self.course.passing_grade:
                struggle_components.append("exams")
            struggle_log = ", ".join(struggle_components) if struggle_components else "none"
            
            data.append({
                'student_id': student_id,
                'name': name,
                'homework_avg': homework_avg,
                'quiz_avg': quiz_avg,
                'exam_grade': exam,
                'final_grade': final_grade,
                'fail_label': fail_label,
                'struggle_log': struggle_log
            })
        
        return pd.DataFrame(data)

# === Predefined Machine Learning Model: Logistic Regression ===

def train_failure_prediction_model(df):
    """
    Trains a logistic regression model on the synthetic data.
    Uses homework, quiz, exam, and final grade as features.
    """
    features = df[['homework_avg', 'quiz_avg', 'exam_grade', 'final_grade']]
    target = df['fail_label']
    
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.3, random_state=42)
    
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Evaluate model performance
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print("Logistic Regression Model Accuracy: {:.2f}%".format(acc * 100))
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    return model

def predict_failure(model, df):
    """Adds a predicted failure probability and a flag for each student to the DataFrame."""
    features = df[['homework_avg', 'quiz_avg', 'exam_grade', 'final_grade']]
    probabilities = model.predict_proba(features)[:, 1]
    df['predicted_failure_prob'] = probabilities
    # Flag students with a predicted probability above a chosen threshold (e.g., 0.5)
    df['flagged'] = df['predicted_failure_prob'] > 0.5
    return df

# === Example Usage ===

if __name__ == "__main__":
    # Example syllabus text (in reality, you could parse this from a PDF)
    syllabus_text = """
    Course Title: Introduction to Data Science
    Grading Policy: Homeworks: 40%, Quizzes: 20%, Exams: 40%
    Passing Grade: 60
    """
    
    # Parse the syllabus and create the Course object
    course = Course(syllabus_text)
    print("Parsed Course Information:")
    print(course)
    
    # Generate synthetic student data for a 10-week period
    generator = StudentDataGenerator(course, weeks=10)
    student_data = generator.generate_student_data(num_students=100)
    print("\nSample Synthetic Student Data:")
    print(student_data.head())
    
    # Train a predefined logistic regression model on the synthetic data
    model = train_failure_prediction_model(student_data)
    
    # Predict failure probability and flag at-risk students
    results = predict_failure(model, student_data)
    print("\nPredicted Failure Probabilities for Students:")
    print(results[['student_id', 'final_grade', 'predicted_failure_prob', 'flagged', 'struggle_log']].head())
