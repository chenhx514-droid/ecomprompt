import json
import hashlib
import httpx
from database import get_connection

class BaseCrawler:
    name = "base"

    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            resp.raise_for_status()
            return resp.text

    def save_to_db(self, items: list):
        if not items:
            return 0
        conn = get_connection()
        count = 0
        for item in items:
            exists = conn.execute(
                "SELECT id FROM prompts WHERE content LIKE ? LIMIT 1",
                (f"%{item['content'][:80]}%",)
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
                    item.get("platform", "小红书"),
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
