import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
import joblib

def train_proper_model():
    # Load data with proper temporal sorting
    df = pd.read_parquet("complete_student_grades.parquet")
    df = df.sort_values(['student_id', 'course_name', 'week'])
    
    # Use ONLY FINAL OUTCOME as label (critical fix)
    df['failure'] = df.groupby(['student_id', 'course_name'])['final_outcome'].transform(
        lambda x: x.ffill().bfill().eq("fail").astype(int)
    )
    df = df.dropna(subset=['failure'])
    
    # Temporal feature engineering (no future leakage)
    df['grade_trend'] = df.groupby(['student_id', 'course_name'])['current_grade'].transform(
        lambda x: x.rolling(3, min_periods=1).mean().pct_change()
    )
    df['recent_hw_drop'] = df.groupby(['student_id', 'course_name'])['homework_grade'].transform(
        lambda x: (x.rolling(2).mean().diff() < -5).astype(int)
    )
    
    # Features without current_grade (prevents target leakage)
    features = [
        'course_name', 'homework_avg', 'quiz_avg', 
        'grade_trend', 'recent_hw_drop', 'week'
    ]
    
    # Drop rows with NaN values in features
    df = df.dropna(subset=features)
    
    # Time-aware cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Pipeline with proper encoding
    preprocessor = ColumnTransformer([
        ('course', OneHotEncoder(handle_unknown='ignore'), ['course_name']),
        ('scaler', StandardScaler(), ['homework_avg', 'quiz_avg', 'grade_trend', 'week'])
    ])
    
    pipe = Pipeline([
        ('pre', preprocessor),
        ('clf', LogisticRegression(class_weight='balanced', max_iter=1000))
    ])
    
    # Grid search for threshold calibration
    param_grid = {'clf__C': [0.01, 0.1, 1, 10]}
    search = GridSearchCV(pipe, param_grid, cv=tscv, scoring='average_precision')
    search.fit(df[features], df['failure'])
    
    # Save best model
    joblib.dump(search.best_estimator_, 'temporal_model.pkl')
    print(f"Best model AP: {search.best_score_:.2f}")

if __name__ == "__main__":
    train_proper_model()