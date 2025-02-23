import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import h5py
import pyarrow as pa
import pyarrow.parquet as pq

def generate_student_grades(num_students=50, current_week=10, seed=42):
    """
    Generate synthetic student grade data with a time-based structure,
    including only data up to the current week
    """
    np.random.seed(seed)
    
    # Course configurations
    courses = {
        'CS182': {
            'weeks': 15,  # Total weeks in semester
            'homework_schedule': {week: f'HW{week}' for week in range(1, 12)},  # One HW per week
            'quiz_schedule': {week: f'Q{week}' for week in range(1, 13)},       # One quiz per week
            'midterm_week': 8,  # Midterm in week 8
            'homework_weight': 25,
            'quiz_weight': 10,
            'exam_weight': 30,
            'passing_percentage': 60
        },
        'MA261': {
            'weeks': 15,
            'homework_schedule': {week: f'HW{week}' for week in range(1, 11)},
            'quiz_schedule': {week: f'Q{week}' for week in range(1, 9)},
            'midterm_week': 7,
            'homework_weight': 20,
            'quiz_weight': 15,
            'exam_weight': 35,
            'passing_percentage': 65
        }
    }

    all_records = []
    
    # Generate base student profiles
    for student_id in range(1, num_students + 1):
        # Assign student characteristics that will affect their performance
        student_ability = np.random.normal(75, 15)  # Base student ability
        
        for course_name, config in courses.items():
            # Create weekly records for each student in each course
            student_performance = []
            
            for week in range(1, config['weeks'] + 1):
                record = {
                    'student_id': f"STU{str(student_id).zfill(4)}",
                    'course_name': course_name,
                    'week': week,
                    'homework_grade': None,
                    'quiz_grade': None,
                    'midterm_grade': None,
                    'homework_avg': None,
                    'quiz_avg': None,
                    'current_grade': None,
                    'failing_probability': None
                }
                
                # Only generate grades up to the current week
                if week <= current_week:
                    # Generate homework grade if scheduled this week
                    if week in config['homework_schedule']:
                        hw_grade = np.random.normal(student_ability + 10, 8)  # Homework tends to be higher
                        record['homework_grade'] = round(max(min(hw_grade, 100), 0), 1)
                    
                    # Generate quiz grade if scheduled this week
                    if week in config['quiz_schedule']:
                        quiz_grade = np.random.normal(student_ability, 12)  # Quizzes more variable
                        record['quiz_grade'] = round(max(min(quiz_grade, 100), 0), 1)
                    
                    # Generate midterm grade
                    if week == config['midterm_week']:
                        midterm_grade = np.random.normal(student_ability - 5, 15)  # Midterm is harder
                        record['midterm_grade'] = round(max(min(midterm_grade, 100), 0), 1)
                    
                    # Calculate running averages
                    valid_hw_grades = [r['homework_grade'] for r in student_performance + [record] 
                                     if r['homework_grade'] is not None]
                    valid_quiz_grades = [r['quiz_grade'] for r in student_performance + [record] 
                                       if r['quiz_grade'] is not None]
                    
                    if valid_hw_grades:
                        record['homework_avg'] = round(np.mean(valid_hw_grades), 1)
                    if valid_quiz_grades:
                        record['quiz_avg'] = round(np.mean(valid_quiz_grades), 1)
                    
                    # Calculate current grade if we have some grades
                    if any([record['homework_avg'], record['quiz_avg'], record['midterm_grade']]):
                        current_grade = 0
                        if record['homework_avg']:
                            current_grade += record['homework_avg'] * (config['homework_weight'] / 100)
                        if record['quiz_avg']:
                            current_grade += record['quiz_avg'] * (config['quiz_weight'] / 100)
                        if record['midterm_grade']:
                            current_grade += record['midterm_grade'] * (config['exam_weight'] / 100)
                        record['current_grade'] = round(current_grade, 1)
                
                student_performance.append(record)
                all_records.extend([record])
    
    # Convert to DataFrame
    df = pd.DataFrame(all_records)
    df = df.sort_values(['student_id', 'course_name', 'week'])
    return df

def save_to_parquet(df, filename='student_grades.parquet'):
    """
    Save the generated grades to a Parquet file
    
    Parquet advantages:
    - Column-oriented storage (efficient for analytical queries)
    - Compression support
    - Schema preservation
    - Faster read/write for large datasets
    """
    # Convert to PyArrow Table
    table = pa.Table.from_pandas(df)
    
    # Write to Parquet with compression
    pq.write_table(table, filename, compression='snappy')
    print(f"Data saved to {filename}")
    
    # Print some metadata about the saved file
    file_metadata = pq.read_metadata(filename)
    print(f"Parquet file size: {file_metadata.serialized_size} bytes")
    print(f"Number of row groups: {file_metadata.num_row_groups}")



def read_from_parquet(filename='student_grades.parquet'):
    """
    Read data from Parquet file
    """
    return pd.read_parquet(filename)


# Example usage
if __name__ == "__main__":
    # Generate grades
    grades_df = generate_student_grades(num_students=60, current_week=10)
    
    # Save to both formats
    save_to_parquet(grades_df)
    
    # Example of reading back the data
    print("\nReading back from Parquet:")
    parquet_df = read_from_parquet()
    print(parquet_df.head())
