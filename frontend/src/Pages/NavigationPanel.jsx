import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Styles/NavigationPanelStyles.css';

export default function NavigationPanel({ onUserClick, selectedUser }) {
    const [users, setUsers] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        axios.get('http://127.0.0.1:5000/api/student-grades')
            .then(response => {
                console.log('Data fetched:', response.data); // Debugging statement
                setUsers(response.data);
                console.log('Users state set:', response.data); // Debugging statement
            })
            .catch(error => {
                console.error('There was an error fetching the student grades!', error);
            });
    }, []);

    console.log('Users:', users); // Debugging statement

    const filteredUsers = Array.isArray(users) ? users.filter(user => {
        console.log('User:', user); // Debugging statement
        const matchesSearchTerm = user.name && user.name.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesFilter = filter === 'all' || user.dotColor === filter;
        console.log('matchesSearchTerm:', matchesSearchTerm); // Debugging statement
        console.log('matchesFilter:', matchesFilter); // Debugging statement
        return matchesSearchTerm && matchesFilter;
    }) : [];

    console.log('Filtered users:', filteredUsers); // Debugging statement

    return (
        <div className="navigationPanel">
            <h1 className="subheadings">All Students</h1>
            <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="searchBar"
            />
            <select value={filter} onChange={(e) => setFilter(e.target.value)} className="filterSelect">
                <option value="all">All</option>
                <option value="green">Passing</option>
                <option value="red">At Risk</option>
            </select>
            <ul className="userList">
                {filteredUsers.map(user => (
                    <li
                        key={user.student_id}
                        onClick={() => onUserClick(user)}
                        className={selectedUser && selectedUser.student_id === user.student_id ? 'active' : ''}
                    >
                        <div className="completeProfile">
                            <img src={user.profilePicture} className="profilePictures" alt="Profile" />
                            <div className="usernamePart">
                                <span className="userName">{user.name}</span>
                                <span className="userSubText">{user.subtext}</span>
                            </div>
                            <div className="dot" style={{ backgroundColor: user.dotColor }}></div>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
}