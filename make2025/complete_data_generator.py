import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict

def generate_complete_student_data(
    output_path: str = "complete_student_grades.parquet",
    num_students: int = 100,
    courses: List[str] = ["CS182", "MA261", "PHY101"],
    weeks: int = 15,
    passing_percentage: float = 60.0,
    random_seed: int = 42
) -> None:
    """
    Generates complete synthetic student data with realistic academic trajectories,
    final outcomes, and failure probabilities.
    """
    np.random.seed(random_seed)
    data = []
    
    # Course weight configuration (align with syllabus)
    weights = {
        "homework": 0.25,
        "quizzes": 0.10,
        "midterm": 0.25,
        "final": 0.40
    }
    
    for student_id in range(1, num_students + 1):
        student_id = f"STU{student_id:04d}"
        for course in courses:
            # Initialize course parameters
            base_skill = np.random.normal(loc=70, scale=15)
            consistency = np.random.beta(a=2, b=2)  # Student consistency factor
            
            # Generate weekly performance
            hw_grades = []
            quiz_grades = []
            current_grades = []
            week_data = []
            
            for week in range(1, weeks + 1):
                # Generate weekly grades with realistic patterns
                hw_noise = np.random.normal(0, 5)
                quiz_noise = np.random.normal(0, 7)
                
                # Homework grades (more consistent)
                hw_grade = max(0, min(100, 
                    base_skill * (1 + 0.02*week) + hw_noise * consistency
                ))
                
                # Quiz grades (more variable)
                quiz_grade = max(0, min(100,
                    base_skill * (0.9 + 0.01*week) + quiz_noise * (1 - consistency)
                ))
                
                # Calculate running averages
                hw_grades.append(hw_grade)
                quiz_grades.append(quiz_grade)
                
                hw_avg = np.mean(hw_grades)
                quiz_avg = np.mean(quiz_grades)
                
                # Calculate current grade projection
                current_grade = (
                    hw_avg * weights["homework"] +
                    quiz_avg * weights["quizzes"] +
                    (base_skill if week < 8 else np.nan) * weights["midterm"] * (week >= 8) +
                    (base_skill if week < 15 else np.nan) * weights["final"] * (week >= 15)
                )
                
                # Add midterm/final grades at appropriate weeks
                midterm = np.nan
                final = np.nan
                if week == 8:
                    midterm = max(0, min(100, base_skill + np.random.normal(0, 10)))
                if week == 15:
                    final = max(0, min(100, 
                        base_skill * (0.9 + 0.1*(week/15)) + np.random.normal(0, 15)
                    ))
                
                # Calculate failure probability using logistic function
                failure_prob = 1 / (1 + np.exp(-(0.5*(passing_percentage - current_grade))))
                
                record = {
                    "student_id": student_id,
                    "course_name": course,
                    "week": week,
                    "homework_grade": hw_grade if week <= weeks else np.nan,
                    "quiz_grade": quiz_grade if week <= weeks else np.nan,
                    "midterm_grade": midterm,
                    "final_exam_grade": final if week == 15 else np.nan,
                    "homework_avg": hw_avg,
                    "quiz_avg": quiz_avg,
                    "current_grade": current_grade,
                    "final_grade": final if week == 15 else np.nan,
                    "final_outcome": (
                        "pass" if (week == 15 and final >= passing_percentage) 
                        else "fail" if week == 15 
                        else None
                    ),
                    "failing_probability": failure_prob
                }
                
                week_data.append(record)
            
            # Backfill final grade and outcome
            final_grade = (
                week_data[-1]["homework_avg"] * weights["homework"] +
                week_data[-1]["quiz_avg"] * weights["quizzes"] +
                week_data[7]["midterm_grade"] * weights["midterm"] +
                week_data[-1]["final_exam_grade"] * weights["final"]
            )
            
            for week in range(weeks):
                week_data[week]["final_grade"] = final_grade if week == 14 else np.nan
                week_data[week]["final_outcome"] = (
                    "pass" if final_grade >= passing_percentage else "fail"
                ) if week == 14 else None
            
            data.extend(week_data)
    
    df = pd.DataFrame(data)
    
    # Convert to optimal data types
    dtypes = {
        "student_id": "category",
        "course_name": "category",
        "week": "int8",
        "homework_grade": "float32",
        "quiz_grade": "float32",
        "midterm_grade": "float32",
        "final_exam_grade": "float32",
        "homework_avg": "float32",
        "quiz_avg": "float32",
        "current_grade": "float32",
        "final_grade": "float32",
        "final_outcome": "category",
        "failing_probability": "float32"
    }
    
    df = df.astype(dtypes)
    
    # Save to Parquet
    df.to_parquet(output_path, index=False)
    print(f"Generated complete dataset with {len(df)} records at {output_path}")

if __name__ == "__main__":
    generate_complete_student_data(
        output_path="complete_student_grades.parquet",
        num_students=1000,  # Generate 1000 student records
        courses=["CS182", "MA261", "PHY101"],
        weeks=15,
        passing_percentage=60.0,
        random_seed=42
    )