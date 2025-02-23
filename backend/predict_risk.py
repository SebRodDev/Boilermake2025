import pandas as pd
import joblib
import numpy as np
from sklearn.calibration import calibration_curve

def get_accurate_risks(week: int, threshold: float = 0.5):
    try:
        pipeline = joblib.load('temporal_model.pkl')
        df = pd.read_parquet("student_grades.parquet")
        
        # Filter only by the week and where failing_probability is not yet set
        current_data = df[
            (df['week'] == week) & 
            (df['failing_probability'].isna())
        ].copy()
        
        # Calculate grade trend using a rolling mean and percentage change
        current_data['grade_trend'] = current_data.groupby('student_id')['current_grade'].transform(
            lambda x: (x.rolling(3, min_periods=1).mean()
                      .pct_change()
                      .fillna(0))
        )
        
        # Calculate if there is a significant drop in recent homework grades
        current_data['recent_hw_drop'] = current_data.groupby('student_id')['homework_grade'].transform(
            lambda x: (x.rolling(2).mean()
                      .diff()
                      .lt(-5)
                      .fillna(0)
                      .astype(int))
        )
        
        required_features = [
            'course_name',
            'homework_avg',
            'quiz_avg',
            'grade_trend',
            'recent_hw_drop',
            'week'
        ]
        
        # Predict the probability of failing
        current_data['failure_prob'] = pipeline.predict_proba(current_data[required_features])[:, 1]
        
        # Identify weakest area for each student
        def identify_weakest_area(row):
            scores = {
                'Homework': row['homework_avg'],
                'Quizzes': row['quiz_avg'],
                'Exams': row['current_grade']  # Assuming this reflects exam performance
            }
            weakest_area = min(scores.items(), key=lambda x: x[1])
            return {
                'weakest_area': weakest_area[0],
                'area_score': weakest_area[1],
                'homework_score': scores['Homework'],
                'quiz_score': scores['Quizzes'],
                'exam_score': scores['Exams']
            }
        
        # Apply the analysis to each student
        weakness_analysis = current_data.apply(identify_weakest_area, axis=1)
        current_data['weakest_area'] = [x['weakest_area'] for x in weakness_analysis]
        current_data['area_score'] = [x['area_score'] for x in weakness_analysis]
        
        # Filter students whose probability exceeds the threshold
        at_risk = current_data[current_data['failure_prob'] >= threshold]
        
        if not at_risk.empty:
            # Add detailed analysis to the output
            result_df = at_risk[[
                'student_id', 
                'course_name', 
                'week', 
                'failure_prob', 
                'weakest_area',
                'area_score',
                'homework_avg',
                'quiz_avg',
                'current_grade'
            ]].copy()
            
            # Add a summary of the weakness
            result_df['weakness_summary'] = result_df.apply(
                lambda x: f"Struggling most with {x['weakest_area']} "
                         f"(Score: {x['area_score']:.1f}%). "
                         f"Performance breakdown - "
                         f"Homework: {x['homework_avg']:.1f}%, "
                         f"Quizzes: {x['quiz_avg']:.1f}%, "
                         f"Exams: {x['current_grade']:.1f}%",
                axis=1
            )
            
            # Save the results
            result_df.to_parquet(f"risks_week{week}.parquet")
            return result_df
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    week = 10
    threshold = 0.65
    at_risk_students = get_accurate_risks(week, threshold)
    
    # Print detailed analysis for each at-risk student
    if not at_risk_students.empty:
        print("\nAt-risk students analysis:")
        for _, student in at_risk_students.iterrows():
            print(f"\nStudent ID: {student['student_id']}")
            print(f"Course: {student['course_name']}")
            print(f"Failure Probability: {student['failure_prob']:.1%}")
            print(f"Analysis: {student['weakness_summary']}")
    else:
        print("No at-risk students found for the given week and threshold.")