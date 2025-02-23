import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np
import os

# Configuration
DATA_PATH = "student_grades.parquet"
PASSING_GRADE = 60
FINAL_OUTCOME_COL = 'final_outcome'  # Use actual final outcomes if available

# Check for model and scaler files
if not os.path.exists("logistic_model.pkl"):
    raise FileNotFoundError("logistic_model.pkl not found.")
if not os.path.exists("scaler.pkl"):
    raise FileNotFoundError("scaler.pkl not found.")

# Load the saved model and scaler
model = joblib.load("logistic_model.pkl")
scaler = joblib.load("scaler.pkl")

def load_and_preprocess():
    # Load without specifying dtype
    df = pd.read_parquet(DATA_PATH)
    
    # Convert data types
    dtype = {
        'student_id': 'category',
        'course_name': 'category',
        'week': 'int8',
        'homework_grade': 'float32',
        'quiz_grade': 'float32',
        'midterm_grade': 'float32',
        'final_exam_grade': 'float32',
        'current_grade': 'float32'
    }
    df = df.astype(dtype)
    
    # Improved missing value handling
    for col in ['midterm_grade', 'final_exam_grade']:
        df[col] = df.groupby('student_id')[col].ffill()
    
    # Create target based on final outcome if available
    if FINAL_OUTCOME_COL in df.columns:
        df['failure'] = (df[FINAL_OUTCOME_COL] == 'fail').astype(int)
    else:  # Fallback to current grade
        df['failure'] = (df['current_grade'] < PASSING_GRADE).astype(int)
    
    # Feature engineering
    df['grade_week_interaction'] = df['current_grade'] * df['week']
    df['assignments_remaining'] = df.groupby('student_id')['week'].transform(
        lambda x: x.max() - x
    )
    
    return df

def compute_failure_probabilities():
    df = load_and_preprocess()
    
    features = [
        'homework_avg', 'quiz_avg', 'current_grade', 
        'week', 'grade_week_interaction', 'assignments_remaining'
    ]
    
    # Ensure columns are numeric
    X_new = df[features].apply(pd.to_numeric, errors="coerce")
    if X_new.isnull().any().any():
        print("Warning: There are still NaNs in the feature columns after conversion.")
    
    # Scale the features
    X_new_scaled = scaler.transform(X_new)
    
    # Predict failure probabilities
    failure_probs = model.predict_proba(X_new_scaled)[:, 1]
    df["failing_probability"] = failure_probs
    
    # Flag students at risk
    df["at_risk"] = df["failing_probability"] > 0.6
    
    # Output students at risk
    at_risk_students = df[df["at_risk"]]
    print(at_risk_students[["student_id", "course_name", "week", "failing_probability"]])
    
    return df

if __name__ == "__main__":
    compute_failure_probabilities()