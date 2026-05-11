from fastapi import APIRouter, Query
from database import get_connection
import json
import os

router = APIRouter()

TREND_CALENDAR_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge", "trend_calendar.json")

@router.get("/trends/hot-categories")
def hot_categories():
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, COUNT(*) as cnt, AVG(trend_score) as avg_score "
        "FROM prompts GROUP BY category ORDER BY avg_score DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return [{"category": r["category"], "count": r["cnt"], "avg_score": round(r["avg_score"], 1)} for r in rows]

@router.get("/trends/keywords")
def hot_keywords(limit: int = Query(20, ge=1, le=100)):
    conn = get_connection()
    rows = conn.execute(
        "SELECT keyword, heat, source FROM trends ORDER BY heat DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [{"keyword": r["keyword"], "heat": r["heat"], "source": r["source"]} for r in rows]

@router.get("/trends/calendar")
def trend_calendar():
    with open(TREND_CALENDAR_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/trends/rising")
def rising_categories():
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, keyword, MAX(heat) as max_heat "
        "FROM trends WHERE source='user_import' "
        "GROUP BY category ORDER BY max_heat DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return [{"category": r["category"], "keyword": r["keyword"], "heat": r["max_heat"]} for r in rows]
