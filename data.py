import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline

class CourseDataGenerator:
    def __init__(self, seed=42):
        """Initialize the data generator with course-specific parameters."""
        np.random.seed(seed)
        
        # Define course-specific characteristics
        self.course_params = {
            'CS182': {
                'difficulty_base': 7,  # Base difficulty level (1-10)
                'grade_mean': 75,      # Mean grade
                'grade_std': 12,       # Grade standard deviation
                'homework_count': 8,   # Number of homework assignments
                'project_weight': 0.4, # Weight of projects in final grade
                'quiz_count': 5,       # Number of quizzes
            },
            'MA261': {
                'difficulty_base': 8,
                'grade_mean': 70,
                'grade_std': 15,
                'homework_count': 12,
                'project_weight': 0.2,
                'quiz_count': 8,
            }
        }

    def generate_student_data(self, num_students_per_course):
        """Generate synthetic student data for multiple courses."""
        all_data = []
        
        for course, params in self.course_params.items():
            # Generate base student characteristics
            student_ability = np.random.normal(0, 1, num_students_per_course)  # Student's inherent ability
            prior_knowledge = np.random.normal(0, 1, num_students_per_course)  # Prior subject knowledge
            
            # Generate course-specific data
            data = {
                'course': course,
                'student_id': [f"{course}_{i}" for i in range(num_students_per_course)],
                
                # Academic metrics
                'midterm_grade': np.clip(
                    params['grade_mean'] + params['grade_std'] * (0.7 * student_ability + 0.3 * prior_knowledge) + 
                    np.random.normal(0, 5, num_students_per_course),
                    0, 100
                ),
                
                'quiz_average': np.clip(
                    params['grade_mean'] + params['grade_std'] * (0.6 * student_ability + 0.4 * np.random.normal(0, 1, num_students_per_course)),
                    0, 100
                ),
                
                # Engagement metrics
                'attendance_rate': np.clip(
                    0.85 + 0.15 * student_ability + np.random.normal(0, 0.1, num_students_per_course),
                    0, 1
                ),
                
                'study_time': np.clip(
                    10 + 5 * (student_ability + np.random.normal(0, 0.5, num_students_per_course)),
                    1, 30
                ),
                
                # Assignment metrics
                'homework_completion_rate': np.clip(
                    0.9 + 0.1 * student_ability + np.random.normal(0, 0.1, num_students_per_course),
                    0, 1
                ),
                
                'submission_lateness': np.clip(
                    -student_ability + np.random.normal(0, 1, num_students_per_course),
                    -2, 5  # Negative means early, positive means late
                ),
                
                # Course-specific metrics
                'course_difficulty': np.full(num_students_per_course, params['difficulty_base']) +
                                   np.random.normal(0, 0.5, num_students_per_course),
                
                'project_score': np.clip(
                    params['grade_mean'] + params['grade_std'] * (0.8 * student_ability + 0.2 * np.random.normal(0, 1, num_students_per_course)),
                    0, 100
                ),
            }
            
            # Calculate final grade based on course-specific weights
            data['final_grade'] = (
                0.3 * data['midterm_grade'] +
                0.2 * data['quiz_average'] +
                params['project_weight'] * data['project_score'] +
                (1 - 0.3 - 0.2 - params['project_weight']) * (100 * data['homework_completion_rate'])
            )
            
            # Calculate failure probability using a more complex model
            failure_factors = (
                -0.03 * data['final_grade'] +
                0.15 * data['submission_lateness'] +
                -0.1 * data['attendance_rate'] * 100 +
                -0.02 * data['study_time'] +
                0.1 * data['course_difficulty'] +
                -0.05 * data['homework_completion_rate'] * 100
            )
            
            data['failure_prob'] = 1 / (1 + np.exp(-failure_factors))
            data['fail_label'] = (data['failure_prob'] > 0.5).astype(int)
            
            all_data.append(pd.DataFrame(data))
        
        return pd.concat(all_data, ignore_index=True)