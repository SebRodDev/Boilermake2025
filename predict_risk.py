import pandas as pd
import joblib
import numpy as np
from sklearn.calibration import calibration_curve

def get_accurate_risks(week: int, course: str, threshold: float = 0.5):
    try:
        pipeline = joblib.load('temporal_model.pkl')
        df = pd.read_parquet("student_grades.parquet")
        
        current_data = df[
            (df['week'] == week) &
            (df['course_name'] == course) &
            (df['failing_probability'].isna())
        ].copy()

        # Fixed lambda syntax with proper parentheses
        current_data['grade_trend'] = current_data.groupby('student_id')['current_grade'].transform(
            lambda x: (x.rolling(3, min_periods=1).mean()
                      .pct_change()
                      .fillna(0))
        )

        current_data['recent_hw_drop'] = current_data.groupby('student_id')['homework_grade'].transform(
            lambda x: (x.rolling(2).mean()
                      .diff()
                      .lt(-5)
                      .fillna(0)
                      .astype(int))
        )

        required_features = [
            'course_name', 'homework_avg', 'quiz_avg', 
            'grade_trend', 'recent_hw_drop', 'week'
        ]

        current_data['failure_prob'] = pipeline.predict_proba(current_data[required_features])[:, 1]

        at_risk = current_data[current_data['failure_prob'] >= threshold]
        if not at_risk.empty:
            at_risk[['student_id', 'course_name', 'week', 'failure_prob']].to_parquet(
                f"risks_{course}_week{week}.parquet"
            )
        return at_risk

    except Exception as e:
        print(f"Error: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Example usage
    week = 10
    course = "CS182"
    threshold = 0.65
    at_risk_students = get_accurate_risks(week, course, threshold)
    print(at_risk_students)