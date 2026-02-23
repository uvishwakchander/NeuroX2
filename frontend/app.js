// API handling for NeuroX2

// Mental Ally API
async function fetchMentalAllyData() {
    const response = await fetch('/api/mental-ally');
    return response.json();
}

// Task Quests API
async function fetchTaskQuests() {
    const response = await fetch('/api/task-quests');
    return response.json();
}

// Burnout Checking API
async function checkBurnout() {
    const response = await fetch('/api/burnout');
    return response.json();
}

// Mood Tracking API
async function trackMood(moodData) {
    const response = await fetch('/api/mood-tracking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(moodData),
    });
    return response.json();
}

// Forum Posts API
async function fetchForumPosts() {
    const response = await fetch('/api/forum-posts');
    return response.json();
}

// Progress Tracking API
async function trackProgress(progressData) {
    const response = await fetch('/api/progress-tracking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(progressData),
    });
    return response.json();
}

// Integrated Features
async function fetchIntegratedFeatures() {
    const response = await fetch('/api/integrated-features');
    return response.json();
}

// Exporting functions for use in other modules
export {
    fetchMentalAllyData,
    fetchTaskQuests,
    checkBurnout,
    trackMood,
    fetchForumPosts,
    trackProgress,
    fetchIntegratedFeatures
};