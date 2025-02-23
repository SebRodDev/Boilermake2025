import React, { useState } from 'react';
import './Styles/NavigationPanelStyles.css';

const users = [
    { id: 1, profilePicture: 'https://t4.ftcdn.net/jpg/03/64/21/11/360_F_364211147_1qgLVxv1Tcq0Ohz3FawUfrtONzz8nq3e.jpg', name: 'User 1', subtext: '4567878', dotColor: 'green', currentGrade: '95%' },
    { id: 2, profilePicture: 'https://i.pinimg.com/736x/a8/4a/a3/a84aa310f33862e53c30f55bdf94b013.jpg', name: 'User 2', subtext: '1234567', dotColor: 'red', currentGrade: '51%' },
    { id: 3, profilePicture: 'https://static.vecteezy.com/system/resources/thumbnails/005/544/718/small_2x/profile-icon-design-free-vector.jpg', name: 'User 3', subtext: '1234567', dotColor: 'green', currentGrade: '75%' },
];

export default function NavigationPanel({ onUserClick, selectedUser }) {
    const [searchTerm, setSearchTerm] = useState('');
    const [filter, setFilter] = useState('all');

    const filteredUsers = users.filter(user => {
        const matchesSearchTerm = user.name.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesFilter = filter === 'all' || user.dotColor === filter;
        return matchesSearchTerm && matchesFilter;
    });

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
                        key={user.id}
                        onClick={() => onUserClick(user)}
                        className={selectedUser && selectedUser.id === user.id ? 'active' : ''}
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