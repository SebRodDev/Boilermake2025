import React from 'react';

function Dashboard({ students, onSelectStudent, selectedStudentId }) {
  const uniqueStudents = [...new Set(students.map(student => student.student_id))];

  return (
    <div className="student-list">
      <h2>At-Risk Students</h2>
      <ul>
        {uniqueStudents.map(studentId => (
          <li 
            key={studentId} 
            className={`student-item ${selectedStudentId === studentId ? 'selected' : ''}`}
            onClick={() => onSelectStudent(studentId)}
          >
            <div className="student-id-container">
              <div className="red-bubble"></div>
              <span className="student-id">{studentId}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Dashboard;