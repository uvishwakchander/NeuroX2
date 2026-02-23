// frontend/app.js

// Import required libraries
import React, { useState, useEffect } from 'react';
import Chat from './components/Chat';
import MoodTracker from './components/MoodTracker';
import QuestGenerator from './components/QuestGenerator';
import BurnoutChecker from './components/BurnoutChecker';
import Forum from './components/Forum';

function App() {
    const [mood, setMood] = useState('');
    const [quests, setQuests] = useState([]);
    const [burnoutLevel, setBurnoutLevel] = useState(null);

    useEffect(() => {
        // Logic for fetching quests or mood data can be added here
    }, []);

    return (
        <div className="App">
            <h1>Welcome to NeuroX2</h1>
            <Chat />
            <MoodTracker mood={mood} setMood={setMood} />
            <QuestGenerator setQuests={setQuests} />
            <BurnoutChecker setBurnoutLevel={setBurnoutLevel} />
            <Forum />
        </div>
    );
}

export default App;