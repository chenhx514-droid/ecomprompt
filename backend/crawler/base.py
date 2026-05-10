import json
import hashlib
import httpx
from database import get_connection

class BaseCrawler:
    name = "base"

    def fetch(self, url: str) -> str:
        """同步 GET 请求"""
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            resp.raise_for_status()
            return resp.text

    def fetch_json(self, url: str) -> dict:
        """同步 GET + 解析JSON"""
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            resp.raise_for_status()
            return resp.json()

    def save_to_db(self, items: list):
        if not items:
            return 0
        conn = get_connection()
        count = 0
        for item in items:
            content_preview = item['content'][:80]
            exists = conn.execute(
                "SELECT id FROM prompts WHERE content LIKE ? LIMIT 1",
                (f"%{content_preview}%",)
            ).fetchone()
            if exists:
                continue

            conn.execute(
                """INSERT INTO prompts
                   (title, category, scenario, platform, content, output_type,
                    preview_images, trend_score, source)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item.get("title", ""),
                    item.get("category", "其他"),
                    item.get("scenario", "日常种草"),
                    item.get("platform", "通用"),
                    item["content"],
                    item.get("output_type", "主图提示词"),
                    json.dumps(item.get("preview_images", [])),
                    item.get("trend_score", 50.0),
                    f"crawler:{self.name}"
                )
            )
            count += 1
        conn.commit()
        conn.close()
        return count

    def run(self) -> int:
        raise NotImplementedError
