import pandas as pd

def process_student_data(week: int, risks_file: str, student_grades_file: str, output_file: str):
    """
    Reads at-risk student IDs, filters student grades, and saves to a new Parquet file.

    Args:
        week (int): The week to filter student grades by.
        risks_file (str): Path to the Parquet file containing at-risk student data.
        student_grades_file (str): Path to the main student grades Parquet file.
        output_file (str): Path to save the filtered student grades Parquet file.
    """
    try:
        # Read at-risk student IDs
        risks_df = pd.read_parquet(risks_file)
        at_risk_student_ids = risks_df['student_id'].unique()

        # Read student grades, filtering out at-risk students and non-target week
        all_grades_df = pd.read_parquet(student_grades_file)
        filtered_grades = all_grades_df[
            (~all_grades_df['student_id'].isin(at_risk_student_ids)) & (all_grades_df['week'] == week)
        ]

        # Save filtered grades to a new Parquet file
        filtered_grades.to_parquet(output_file)
        print(f"Filtered student grades saved to {output_file}")

    except FileNotFoundError:
        print("Error: One or both input files not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    week = 10
    risks_file = f"risks_week{week}.parquet"  # Assuming the output file from the previous script
    student_grades_file = "student_grades.parquet"
    output_file = f"filtered_student_grades_week{week}.parquet"

    process_student_data(week, risks_file, student_grades_file, output_file)