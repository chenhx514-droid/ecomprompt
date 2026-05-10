"""Runninghub 爬虫 — 抓取 runninghub.cn 的提示词和效果图"""

from .base import BaseCrawler

class RunninghubCrawler(BaseCrawler):
    name = "runninghub"

    # Runninghub 可能的 API 端点
    URLS = [
        "https://www.runninghub.cn/api/community/images?page=1&pageSize=20",
        "https://www.runninghub.cn/api/workflow/gallery?page=1&pageSize=20",
    ]

    def run(self) -> int:
        import httpx

        for url in self.URLS:
            try:
                with httpx.Client(timeout=15) as client:
                    resp = client.get(url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "application/json",
                    })
                    resp.raise_for_status()
                    data = resp.json()
                    return self._parse_response(data)
            except Exception as e:
                print(f"[runninghub] {url[:50]} failed: {e}")
                continue
        return 0

    def _parse_response(self, data: dict) -> int:
        items = []
        image_list = (
            data.get("data", {}).get("items", []) or
            data.get("data", {}).get("list", []) or
            data.get("data", {}).get("rows", []) or
            data.get("data", []) or
            []
        )

        for img in image_list:
            prompt = img.get("prompt") or img.get("promptText") or ""
            if not prompt or len(prompt) < 15:
                continue

            img_url = img.get("imageUrl") or img.get("coverUrl") or img.get("url", "")
            preview = [img_url] if img_url else []

            title = (img.get("title") or img.get("name") or prompt)[:60]
            likes = img.get("likes") or img.get("likeCount") or 0
            trend = min(100, max(10, int(likes) / 5))

            items.append({
                "title": title,
                "content": prompt,
                "category": self._classify(prompt),
                "scenario": "日常种草",
                "platform": "通用",
                "output_type": "主图提示词",
                "preview_images": preview,
                "trend_score": trend,
            })

        return self.save_to_db(items)

    def _classify(self, text: str) -> str:
        t = text.lower()
        for kw, cat in [
            ("dress", "服饰"), ("fashion", "服饰"), ("clothing", "服饰"),
            ("makeup", "美妆"), ("cosmetic", "美妆"), ("skincare", "美妆"),
            ("phone", "3C数码"), ("laptop", "3C数码"), ("headphone", "3C数码"),
            ("food", "食品"), ("cake", "食品"), ("dessert", "食品"),
            ("furniture", "家居"), ("interior", "家居"), ("home", "家居"),
            ("baby", "母婴"), ("toy", "母婴"), ("kids", "母婴"),
            ("sport", "运动户外"), ("outdoor", "运动户外"), ("running", "运动户外"),
        ]:
            if kw in t:
                return cat
        return "其他"
