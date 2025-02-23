import React from 'react';

function StudentDetails({ studentData }) {
  if (!studentData.length) {
    return <div className="student-details">Select a student to view details</div>;
  }

  return (
    <div className="student-details">
      <h2 className="student-name">{studentData[0].student_id}</h2>
      {studentData.map(student => (
        <div key={student.course_name} className="course-info">
          <h3>Course: {student.course_name}</h3>
          <div className="risk-assessment">
            <h3>Risk Assessment</h3>
            <div className="risk-item">
              <span>Failing Probability:</span>
              <span>{(student.failure_prob * 100).toFixed(2)}%</span>
            </div>
            <div className="risk-item">
              <span>Weakest Area:</span>
              <span>{student.weakest_area}</span>
            </div>
            <div className="risk-item">
              <span>Area Score:</span>
              <span>{student.area_score}%</span>
            </div>
            <div className="risk-item">
              <span>Homework Average:</span>
              <span>{student.homework_avg}%</span>
            </div>
            <div className="risk-item">
              <span>Quiz Average:</span>
              <span>{student.quiz_avg}%</span>
            </div>
            <div className="risk-item">
              <span>Current Grade:</span>
              <span>{student.current_grade}%</span>
            </div>
            <div className="weakness-summary">
              <span>Weakness Summary:</span>
              <span>{student.weakness_summary}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default StudentDetails;