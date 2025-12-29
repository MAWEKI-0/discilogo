"""
Discilogo Database Module - Supabase Version
Cloud-hosted PostgreSQL database for habit tracking.
"""

import streamlit as st
from supabase import create_client, Client
from datetime import date
from typing import Optional

@st.cache_resource
def get_supabase_client() -> Client:
    """Get cached Supabase client."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


def get_client() -> Client:
    """Get Supabase client instance."""
    return get_supabase_client()


# ============== HABIT CRUD ==============

def add_habit(question_text: str) -> int:
    """Add a new habit and return its ID."""
    client = get_client()
    result = client.table("habits").insert({
        "question_text": question_text,
        "is_active": True
    }).execute()
    return result.data[0]["id"]


def get_active_habits() -> list[dict]:
    """Get all active habits."""
    client = get_client()
    result = client.table("habits")\
        .select("id, question_text, created_at")\
        .eq("is_active", True)\
        .order("created_at")\
        .execute()
    return result.data


def get_all_habits() -> list[dict]:
    """Get all habits (active and archived)."""
    client = get_client()
    result = client.table("habits")\
        .select("id, question_text, is_active, created_at")\
        .order("is_active", desc=True)\
        .order("created_at")\
        .execute()
    return result.data


def archive_habit(habit_id: int):
    """Archive a habit (set is_active to False)."""
    client = get_client()
    client.table("habits")\
        .update({"is_active": False})\
        .eq("id", habit_id)\
        .execute()


def delete_habit(habit_id: int):
    """Permanently delete a habit (logs cascade delete)."""
    client = get_client()
    client.table("habits").delete().eq("id", habit_id).execute()


# ============== LOGGING ==============

def log_habit(habit_id: int, habit_question: str, status: bool, excuse_note: Optional[str] = None):
    """Log a habit completion for today."""
    today = date.today().isoformat()
    client = get_client()
    client.table("logs").insert({
        "date": today,
        "habit_id": habit_id,
        "habit_question_snapshot": habit_question,
        "status": status,
        "excuse_note": excuse_note
    }).execute()


def get_pending_habits_today() -> list[dict]:
    """Get active habits that haven't been logged today."""
    today = date.today().isoformat()
    client = get_client()
    
    # Get all active habits
    active_habits = client.table("habits")\
        .select("id, question_text")\
        .eq("is_active", True)\
        .order("created_at")\
        .execute().data
    
    # Get habit IDs logged today
    logged_today = client.table("logs")\
        .select("habit_id")\
        .eq("date", today)\
        .execute().data
    logged_ids = {log["habit_id"] for log in logged_today}
    
    # Filter out logged habits
    pending = [h for h in active_habits if h["id"] not in logged_ids]
    return pending


def get_today_logs() -> list[dict]:
    """Get all logs for today."""
    today = date.today().isoformat()
    client = get_client()
    result = client.table("logs")\
        .select("habit_question_snapshot, status, excuse_note")\
        .eq("date", today)\
        .order("timestamp")\
        .execute()
    return result.data


def get_recent_logs(limit: int = 10) -> list[dict]:
    """Get the most recent log entries."""
    client = get_client()
    result = client.table("logs")\
        .select("id, timestamp, date, habit_question_snapshot, status, excuse_note")\
        .order("timestamp", desc=True)\
        .limit(limit)\
        .execute()
    return result.data


def get_streak() -> int:
    """Calculate the current streak of days with all habits completed (all YES)."""
    client = get_client()
    
    # Get all logs grouped by date, ordered by most recent
    result = client.table("logs")\
        .select("date, status")\
        .order("date", desc=True)\
        .execute()
    
    if not result.data:
        return 0
    
    # Group by date
    date_stats = {}
    for log in result.data:
        d = log["date"]
        if d not in date_stats:
            date_stats[d] = {"total": 0, "successes": 0}
        date_stats[d]["total"] += 1
        if log["status"]:
            date_stats[d]["successes"] += 1
    
    # Calculate streak
    streak = 0
    for d in sorted(date_stats.keys(), reverse=True):
        stats = date_stats[d]
        if stats["total"] == stats["successes"] and stats["total"] > 0:
            streak += 1
        else:
            break
    
    return streak
