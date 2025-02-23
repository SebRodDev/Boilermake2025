import React, { useState } from 'react';
import './Styles/DashboardStyles.css';
import NavigationPanel from './NavigationPanel';
import EmailModal from './EmailModal';

export default function Dashboard() {
    const [selectedUser, setSelectedUser] = useState(null);
    const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);

    const handleUserClick = (user) => {
        setSelectedUser(user);
    };

    const handleSendEmailClick = () => {
        setIsEmailModalOpen(true);
    };

    const handleCloseEmailModal = () => {
        setIsEmailModalOpen(false);
    };

    return (
        <div className="dashboard">
            <NavigationPanel onUserClick={handleUserClick} selectedUser={selectedUser} />
            <div className="content">
                <div className="topBar">
                    <h2 className="title">Student Performance</h2>
                    <button className="sendEmail" type="button" onClick={handleSendEmailClick}>Send Email</button>
                    <img
                        src="https://tr.rbxcdn.com/180DAY-d04a9468177b152ea023e3ac58eafeb6/420/420/Hat/Webp/noFilter"
                        alt="Profile"
                        className="profilePicture"
                    />
                </div>
                {selectedUser && (
                    <div className="detailsAndGraph">
                        <div className="userDetails">
                            <div className="userDetailsBox">
                                <img src={selectedUser.profilePicture} alt="Profile" className="userProfilePicture" />
                                <h3 className="fontSizes">{selectedUser.name}'s Progress</h3>
                            </div>
                            <div className="userDetailBox">
                                <h3 className="smallHeading">Student ID</h3>
                                <p className="largerText">{selectedUser.subtext}</p>
                                <p className="smallerText">{selectedUser.name}</p>
                            </div>
                            <div className="userDetailBox">
                                <h3 className="smallHeading">Current Grade</h3>
                                <p className="largerText">{selectedUser.currentGrade}</p>
                            </div>
                        </div>

                        <div className="graphPlusClasses">
                            <div className="graph">
                                <img
                                    src="https://media.eagereyes.org/wp-content/uploads/2020/11/time-line.png"
                                    alt="Graph"
                                    className="graphImage"
                                />
                            </div>
                            <div className="currentClasses">
                                <h3 className="smallHeading">All Classes</h3>
                                <h4 className="otherText">Other</h4>
                                <h4 className="gradeText">Grade</h4>
                            </div>
                        </div>

                        <div className="failedStatus">
                            <h3 className="smallHeading">Passing Progress</h3>
                            {selectedUser.dotColor === 'red' && (
                                <p className="atRiskText">Student is at risk</p>
                            )}
                            {selectedUser.dotColor === 'green' && (
                                <p className="passingText">Student is passing</p>
                            )}
                        </div>
                    </div>
                )}
            </div>
            <EmailModal
                isOpen={isEmailModalOpen}
                onClose={handleCloseEmailModal}
                selectedUser={selectedUser}
            />
        </div>
    );
}