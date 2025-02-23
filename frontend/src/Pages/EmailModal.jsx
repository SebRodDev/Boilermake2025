import React, { useState, useEffect } from 'react';
import './Styles/EmailModalStyles.css';
import { addEvent } from './googleCalendar';

export default function EmailModal({ isOpen, onClose, selectedUser }) {
    const [emailContent, setEmailContent] = useState('');
    const [eventTitle, setEventTitle] = useState('');
    const [eventDate, setEventDate] = useState('');
    const [eventTime, setEventTime] = useState('');

    const handleAddEvent = async () => {
        const event = {
            summary: eventTitle,
            description: emailContent,
            start: {
                dateTime: `${eventDate}T${eventTime}:00`,
                timeZone: 'America/New_York',
            },
            end: {
                dateTime: `${eventDate}T${eventTime}:00`,
                timeZone: 'America/New_York',
            },
        };

        await addEvent(event);
        onClose();
    };

    const handleClickOutside = (event) => {
        if (event.target.className === 'modalOverlay') {
            onClose();
        }
    };

    useEffect(() => {
        if (isOpen) {
            document.addEventListener('click', handleClickOutside);
        } else {
            document.removeEventListener('click', handleClickOutside);
        }

        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    }, [isOpen]);

    if (!isOpen) {
        return null;
    }

    return (
        <div className="modalOverlay">
            <div className="modalContent">
                <h2>Add Reminder to Google Calendar to meet with {selectedUser.name}</h2>
                <input
                    type="text"
                    value={eventTitle}
                    onChange={(e) => setEventTitle(e.target.value)}
                    placeholder="Event Title"
                />
                <textarea
                    value={emailContent}
                    onChange={(e) => setEmailContent(e.target.value)}
                    placeholder="Event Description"
                />
                <input
                    type="date"
                    value={eventDate}
                    onChange={(e) => setEventDate(e.target.value)}
                />
                <input
                    type="time"
                    value={eventTime}
                    onChange={(e) => setEventTime(e.target.value)}
                />
                <div className="modalActions">
                    <button onClick={handleAddEvent}>Add Event</button>
                    <button onClick={onClose}>Cancel</button>
                </div>
            </div>
        </div>
    );
}