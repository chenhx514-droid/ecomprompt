from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from database import get_connection
import json
import os
import threading

scheduler = BackgroundScheduler()

CALENDAR_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "trend_calendar.json")

def update_trend_scores():
    conn = get_connection()
    now = datetime.now()

    calendar_data = {}
    if os.path.exists(CALENDAR_PATH):
        with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
            calendar_data = json.load(f)

    boost_categories = {}
    for fest in calendar_data.get("festivals", []):
        fest_date = datetime(now.year, fest["month"], fest["day"])
        days_until = (fest_date - now).days
        if 0 <= days_until <= fest["lead_days"]:
            remaining_ratio = days_until / max(fest["lead_days"], 1)
            season_weight = fest["weight"] * (1 + (1 - remaining_ratio))
            for cat in fest["categories"]:
                if cat == "全品类":
                    for c in ["服饰","美妆","3C数码","食品","家居","母婴","运动户外","珠宝饰品"]:
                        boost_categories[c] = max(boost_categories.get(c, 1.0), season_weight)
                else:
                    boost_categories[cat] = max(boost_categories.get(cat, 1.0), season_weight)

    for seasonal in calendar_data.get("seasonal", []):
        if now.month in seasonal["months"]:
            for boosted in seasonal.get("boost_categories", []):
                cat = boosted.split("-")[0]
                boost_categories[cat] = max(boost_categories.get(cat, 1.0), 1.15)

    for category, boost in boost_categories.items():
        conn.execute(
            "UPDATE prompts SET trend_score = MIN(100, trend_score * ?) WHERE category = ?",
            (boost, category)
        )

    decay_date = (now - timedelta(days=30)).isoformat()
    conn.execute(
        "UPDATE prompts SET trend_score = MAX(10, trend_score - 5) WHERE updated_at < ?",
        (decay_date,)
    )

    conn.commit()
    conn.close()

def crawl_all():
    from crawler import CRAWLERS
    total = 0
    for name, crawler in CRAWLERS.items():
        try:
            count = crawler.run()
            total += count
            print(f"[crawler] {name}: {count} items")
        except Exception as e:
            print(f"[crawler] {name} failed: {e}")
    return total

def cleanup_low_quality():
    conn = get_connection()
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    conn.execute("DELETE FROM prompts WHERE updated_at < ? AND trend_score < 15", (cutoff,))
    conn.commit()
    conn.close()

def start_scheduler():
    scheduler.add_job(crawl_all, IntervalTrigger(hours=3), id="crawl", replace_existing=True)
    scheduler.add_job(update_trend_scores, IntervalTrigger(hours=6), id="trend_score", replace_existing=True)
    scheduler.add_job(cleanup_low_quality, CronTrigger(hour=3, minute=0), id="cleanup", replace_existing=True)
    scheduler.start()

    def initial_crawl():
        crawl_all()
    t = threading.Thread(target=initial_crawl)
    t.start()
