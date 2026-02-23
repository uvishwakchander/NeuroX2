from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai
import os
import json
from datetime import datetime
from typing import Optional, List
from enum import Enum

# =============== APP SETUP ===============
app = FastAPI(
    title="NeuroX AI Assistant",
    description="Neurodiversity-friendly AI companion",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============== GEMINI API ===============
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Please set the GEMINI_API_KEY environment variable.")

client = genai.Client(api_key=API_KEY)

# =============== STORAGE (MVP) ===============
forum_posts = []
user_progress = {}
mood_history = []
task_history = []

# =============== MODELS ===============
class BurnoutLevel(str, Enum):
    LOW = "✅ Balanced"
    MODERATE = "⚠️ Moderate load"
    HIGH = "🚨 High load"

class ClarifyInput(BaseModel):
    text: str = Field(..., min_length=1, description="Message to clarify")
    tone: Optional[str] = Field(default="professional", description="Desired tone: casual, professional, friendly")

class TaskInput(BaseModel):
    task: str = Field(..., min_length=1, description="Task to convert into a quest")
    priority: Optional[str] = Field(default="medium", description="Priority level: low, medium, high")
    estimated_time: Optional[int] = Field(default=30, description="Estimated time in minutes")

class BurnoutInput(BaseModel):
    hours_worked: int = Field(..., ge=0, description="Hours worked today")
    tasks_done: int = Field(..., ge=0, description="Tasks completed")
    breaks_taken: int = Field(..., ge=0, description="Number of breaks taken")
    mood: Optional[str] = Field(default="neutral", description="Current mood")

class AllyInput(BaseModel):
    message: str = Field(..., min_length=1, description="Message for the mental ally")
    context: Optional[str] = Field(default=None, description="Additional context")

class ForumPost(BaseModel):
    content: str = Field(..., min_length=1, description="Forum post content")
    author: Optional[str] = Field(default="Anonymous", description="Author name")
    topic: Optional[str] = Field(default="general", description="Topic category")

class MoodEntry(BaseModel):
    mood: str = Field(..., description="Current mood")
    notes: Optional[str] = Field(default=None, description="Optional notes")

class ProgressEntry(BaseModel):
    user_id: str = Field(..., description="User identifier")
    xp_earned: int = Field(..., ge=0, description="Experience points earned")
    tasks_completed: int = Field(..., ge=0, description="Tasks completed")
    streak: int = Field(..., ge=0, description="Current streak")

# =============== HELPER FUNCTIONS ===============
def get_current_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def safe_api_call(prompt: str, model: str = "gemini-1.5-flash"):
    """Safely call Gemini API with error handling"""
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"API Error: {str(e)}")
        return None

# =============== ENDPOINTS: HEALTH ===============
@app.get("/", tags=["Health"])
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "NeuroX AI Brain",
        "timestamp": get_current_timestamp()
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api_connected": API_KEY is not None,
        "timestamp": get_current_timestamp()
    }

# =============== ENDPOINTS: COMMUNICATION COPILOT ===============
@app.post("/clarify", tags=["Communication"])
def clarify_message(data: ClarifyInput):
    """
    Rewrite a message to be clear, kind, professional, and neurodiversity-friendly.
    
    Features:
    - Adjustable tone (casual, professional, friendly)
    - Stress-reducing language
    - Neurodiversity-aware phrasing
    """
    prompt = f"""
    Rewrite this message to be:
    - Clear and concise
    - Kind and empathetic
    - {data.tone}
    - Neurodiversity-friendly
    - Low stress
    - Easy to understand
    
    Original message:
    "{data.text}"
    
    Provide only the rewritten message, no explanation.
    """
    
    result = safe_api_call(prompt)
    
    if result:
        return {
            "original": data.text,
            "clarified": result,
            "tone": data.tone,
            "timestamp": get_current_timestamp()
        }
    else:
        return {
            "original": data.text,
            "clarified": "I'm feeling a bit overwhelmed right now. When you have time, I'd appreciate your support.",
            "tone": data.tone,
            "timestamp": get_current_timestamp(),
            "error": "API temporarily unavailable"
        }

# =============== ENDPOINTS: TASK → QUEST ===============
@app.post("/quest", tags=["Gamification"])
def generate_quest(data: TaskInput):
    """
    Transform a task into a motivating quest with gamification elements.
    
    Features:
    - Gentle, encouraging framing
    - XP rewards based on difficulty
    - Time estimates
    - Priority-based progression
    """
    xp_rewards = {"low": 5, "medium": 10, "high": 25}
    xp = xp_rewards.get(data.priority, 10)
    
    prompt = f"""
    Transform this task into a gentle, motivating quest.
    Priority: {data.priority}
    Estimated time: {data.estimated_time} minutes
    
    Task: "{data.task}"
    
    Create a quest description that:
    - Uses encouraging, gaming-style language
    - Breaks it into small, manageable steps (if needed)
    - Acknowledges the difficulty
    - Motivates without pressure
    
    Format: Start with an emoji, then the quest description.
    """
    
    result = safe_api_call(prompt)
    
    if result:
        return {
            "quest": result,
            "xp": xp,
            "priority": data.priority,
            "estimated_time": data.estimated_time,
            "timestamp": get_current_timestamp()
        }
    else:
        return {
            "quest": f"🌱 {data.task}. One step at a time. You've got this!",
            "xp": xp,
            "priority": data.priority,
            "estimated_time": data.estimated_time,
            "timestamp": get_current_timestamp(),
            "error": "API temporarily unavailable"
        }

# =============== ENDPOINTS: BURNOUT CHECK ===============
@app.post("/burnout", tags=["Wellness"])
def check_burnout(data: BurnoutInput):
    """
    Assess burnout risk based on work metrics.
    
    Scoring:
    - score >= 6: High load
    - score >= 3: Moderate load
    - score < 3: Balanced
    """
    # Calculate burnout score
    # Higher hours, fewer breaks = higher score
    # More tasks completed = lower score (achievement buffer)
    score = (data.hours_worked / (data.breaks_taken + 1)) - (data.tasks_done * 0.5)
    
    if score >= 6:
        status = BurnoutLevel.HIGH
        suggestion = "🚨 Strongly recommend rest. Your wellbeing is priority. Consider stepping back."
        color = "red"
    elif score >= 3:
        status = BurnoutLevel.MODERATE
        suggestion = "⚠️ Consider a short break. You're working hard—take care of yourself."
        color = "yellow"
    else:
        status = BurnoutLevel.LOW
        suggestion = "✅ You're maintaining balance. Keep it up!"
        color = "green"
    
    # Store mood for history
    mood_history.append({
        "timestamp": get_current_timestamp(),
        "mood": data.mood,
        "burnout_score": score,
        "status": status
    })
    
    return {
        "status": status,
        "burnout_score": round(score, 2),
        "suggestion": suggestion,
        "breakdown": {
            "hours_worked": data.hours_worked,
            "tasks_done": data.tasks_done,
            "breaks_taken": data.breaks_taken,
            "mood": data.mood
        },
        "timestamp": get_current_timestamp()
    }

@app.get("/mood-history", tags=["Wellness"])
def get_mood_history(limit: int = Query(10, ge=1, le=100)):
    """Get recent mood and burnout history"""
    return {
        "mood_history": mood_history[-limit:],
        "count": len(mood_history[-limit:])
    }

# =============== ENDPOINTS: MENTAL ALLY ===============
@app.post("/mental-ally", tags=["Support"])
def mental_ally(data: AllyInput):
    """
    Get empathetic, validating responses from a mental health ally.
    
    Features:
    - Non-clinical support
    - Validation and empathy
    - Calming language
    - No diagnosis or medical advice
    """
    context_part = f"\nAdditional context: {data.context}" if data.context else ""
    
    prompt = f"""
    You are a kind Mental Ally—compassionate, non-judgmental, and supportive.
    Your role:
    - Validate their feelings
    - Be empathetic and understanding
    - Offer calming perspective
    - Never provide medical/clinical advice
    - Never diagnose
    - Encourage self-compassion
    
    User message: "{data.message}"{context_part}
    
    Respond with warmth and genuine care. Keep it brief (2-3 sentences).
    """
    
    result = safe_api_call(prompt)
    
    if result:
        return {
            "reply": result,
            "timestamp": get_current_timestamp(),
            "disclaimer": "This is supportive conversation, not medical advice."
        }
    else:
        return {
            "reply": "Thank you for sharing. Your feelings are valid. You're not alone, and it's okay to take things gently.",
            "timestamp": get_current_timestamp(),
            "error": "API temporarily unavailable"
        }

# =============== ENDPOINTS: MOOD TRACKING ===============
@app.post("/mood", tags=["Wellness"])
def log_mood(entry: MoodEntry):
    """Log mood and optional notes for tracking"""
    mood_entry = {
        "timestamp": get_current_timestamp(),
        "mood": entry.mood,
        "notes": entry.notes
    }
    mood_history.append(mood_entry)
    
    return {
        "status": "logged",
        "entry": mood_entry,
        "total_entries": len(mood_history)
    }

# =============== ENDPOINTS: FORUM ===============
@app.post("/forum/post", tags=["Community"])
def post_forum(post: ForumPost):
    """Create a new forum post"""
    forum_entry = {
        "id": len(forum_posts),
        "content": post.content,
        "author": post.author,
        "topic": post.topic,
        "timestamp": get_current_timestamp(),
        "likes": 0
    }
    forum_posts.append(forum_entry)
    
    return {
        "status": "posted",
        "post_id": forum_entry["id"],
        "timestamp": forum_entry["timestamp"]
    }

@app.get("/forum/posts", tags=["Community"])
def get_forum(topic: Optional[str] = None, limit: int = Query(50, ge=1, le=500)):
    """Get forum posts with optional filtering"""
    posts = forum_posts
    
    if topic:
        posts = [p for p in posts if p.get("topic") == topic]
    
    return {
        "posts": posts[-limit:],
        "count": len(posts[-limit:]),
        "total": len(posts)
    }

@app.get("/forum/topics", tags=["Community"])
def get_forum_topics():
    """Get list of all forum topics"""
    topics = list(set(p.get("topic", "general") for p in forum_posts))
    return {
        "topics": topics,
        "count": len(topics)
    }

# =============== ENDPOINTS: PROGRESS TRACKING ===============
@app.post("/progress", tags=["Progress"])
def update_progress(progress: ProgressEntry):
    """Track user progress and achievements"""
    if progress.user_id not in user_progress:
        user_progress[progress.user_id] = {
            "total_xp": 0,
            "total_tasks": 0,
            "max_streak": 0,
            "entries": []
        }
    
    user_data = user_progress[progress.user_id]
    user_data["total_xp"] += progress.xp_earned
    user_data["total_tasks"] += progress.tasks_completed
    user_data["max_streak"] = max(user_data["max_streak"], progress.streak)
    user_data["entries"].append({
        "timestamp": get_current_timestamp(),
        "xp": progress.xp_earned,
        "tasks": progress.tasks_completed,
        "streak": progress.streak
    })
    
    return {
        "status": "updated",
        "user_id": progress.user_id,
        "total_xp": user_data["total_xp"],
        "total_tasks": user_data["total_tasks"],
        "max_streak": user_data["max_streak"]
    }

@app.get("/progress/{user_id}", tags=["Progress"])
def get_progress(user_id: str):
    """Get user progress and stats"""
    if user_id not in user_progress:
        return {
            "user_id": user_id,
            "total_xp": 0,
            "total_tasks": 0,
            "max_streak": 0,
            "entries": []
        }
    
    return {
        "user_id": user_id,
        **user_progress[user_id]
    }

# =============== ENDPOINTS: STATISTICS ===============
@app.get("/stats", tags=["Analytics"])
def get_stats():
    """Get overall platform statistics"""
    total_users = len(user_progress)
    total_xp = sum(u["total_xp"] for u in user_progress.values())
    total_tasks = sum(u["total_tasks"] for u in user_progress.values())
    
    return {
        "total_users": total_users,
        "total_xp_earned": total_xp,
        "total_tasks_completed": total_tasks,
        "forum_posts": len(forum_posts),
        "mood_entries": len(mood_history),
        "timestamp": get_current_timestamp()
    }

# =============== ERROR HANDLING ===============
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": get_current_timestamp()
    }

# =============== ROOT ===============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)