import math

def dict_to_array(data):
    """
    Converts a list of dictionaries into a list of lists (array).

    Args:
        data: A list of dictionaries.

    Returns:
        A list of lists, where each inner list represents a dictionary's values.
    """
    result = []
    for item in data:
        row = []
        for value in item.values():
            if isinstance(value, float) and math.isnan(value):
                row.append(None)  # Replace NaN with None for consistency
            else:
                row.append(value)
        result.append(row)
    return result

# Example usage with your provided data:
data = [
    {
        "course_name": "CS182",
        "current_grade": 30.8,
        "dotColor": "green",
        "failing_probability": None,
        "homework_avg": 91.6,
        "homework_grade": 100.0,
        "midterm_grade": float('nan'),
        "name": "Student STU0001",
        "profilePicture": "https://wallpapers.com/images/hd/generic-person-icon-profile-ulmsmhnz0kqafcqn-2.jpg",
        "quiz_avg": 78.6,
        "quiz_grade": 79.7,
        "student_id": "STU0001",
        "subtext": "Course: CS182, Week: 10",
        "week": 10
    },
    {
        "course_name": "MA261",
        "current_grade": 29.6,
        "dotColor": "green",
        "failing_probability": None,
        "homework_avg": 90.0,
        "homework_grade": 98.4,
        "midterm_grade": float('nan'),
        "name": "Student STU0001",
        "profilePicture": "https://wallpapers.com/images/hd/generic-person-icon-profile-ulmsmhnz0kqafcqn-2.jpg",
        "quiz_avg": 77.4,
        "quiz_grade": float('nan'),
        "student_id": "STU0001",
        "subtext": "Course: MA261, Week: 10",
        "week": 10
    },
    {
        "course_name": "CS182",
        "current_grade": 29.1,
        "dotColor": "green",
        "failing_probability": None,
        "homework_avg": 86.7,
        "homework_grade": 86.1,
        "midterm_grade": float('nan'),
        "name": "Student STU0002",
        "profilePicture": "https://wallpapers.com/images/hd/generic-person-icon-profile-ulmsmhnz0kqafcqn-2.jpg",
        "quiz_avg": 74.6,
        "quiz_grade": 64.3,
        "student_id": "STU0002",
        "subtext": "Course: CS182, Week: 10",
        "week": 10
    }
]

array_result = dict_to_array(data)
print(array_result)