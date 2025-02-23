import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import StudentDetails from './components/StudentDetails';
import './styles.css';

function App() {
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    fetch('http://127.0.0.1:5000/api/students')
      .then(response => response.json())
      .then(data => {
        setStudents(data);
        setIsLoading(false);
      })
      .catch(err => {
        console.error('Error fetching students:', err);
        setIsLoading(false);
      });
  }, []);

  const handleStudentSelect = (studentId) => {
    setSelectedStudentId(studentId);
  };

  const selectedStudentData = students.filter(student => student.student_id === selectedStudentId);

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="app">
      <Dashboard 
        students={students} 
        onSelectStudent={handleStudentSelect}
        selectedStudentId={selectedStudentId}
      />
      {selectedStudentId ? (
        <StudentDetails studentData={selectedStudentData} />
      ) : (
        <div className="empty-state">
          <h2>Select a Student</h2>
          <p>Choose a student from the list to view their details</p>
        </div>
      )}
    </div>
  );
}

export default App;