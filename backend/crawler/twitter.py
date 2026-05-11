"""Twitter/X 爬虫 — 搜索电商AI提示词相关推文"""
import json
import httpx
from .base import BaseCrawler

# Twitter 公开 API (内嵌在 Twitter 网页应用中的 bearer token)
TWITTER_BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"


class TwitterCrawler(BaseCrawler):
    name = "twitter"

    SEARCH_QUERIES = [
        "GPT Image prompt ecommerce",
        "ChatGPT image generation product photography prompt",
        "AI image prompt product shot",
        "gpt-image ecommerce product",
        "AI电商主图提示词",
        "GPT Image 电商",
    ]

    def run(self) -> int:
        try:
            guest_token = self._get_guest_token()
            if not guest_token:
                print("[twitter] Failed to get guest token, using fallback")
                return self._fallback()

            total = 0
            for query in self.SEARCH_QUERIES[:3]:
                try:
                    count = self._search(query, guest_token)
                    total += count
                except Exception as e:
                    print(f"[twitter] search '{query[:30]}' failed: {e}")
                    continue

            if total == 0:
                print("[twitter] No results from API, using fallback")
                return self._fallback()

            return total

        except Exception as e:
            print(f"[twitter] Error: {e}")
            return self._fallback()

    def _get_guest_token(self) -> str | None:
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.post(
                    "https://api.twitter.com/1.1/guest/activate.json",
                    headers={"Authorization": f"Bearer {TWITTER_BEARER}"}
                )
                if resp.status_code == 200:
                    return resp.json().get("guest_token")
        except Exception as e:
            print(f"[twitter] guest token error: {e}")
        return None

    def _search(self, query: str, guest_token: str) -> int:
        params = {
            "q": f"{query} -is:retweet",
            "count": 20,
            "tweet_mode": "extended",
            "result_type": "popular",
        }
        headers = {
            "Authorization": f"Bearer {TWITTER_BEARER}",
            "x-guest-token": guest_token,
        }

        with httpx.Client(timeout=15) as client:
            resp = client.get(
                "https://api.twitter.com/1.1/search/tweets.json",
                params=params,
                headers=headers
            )
            if resp.status_code != 200:
                return 0
            data = resp.json()

        items = []
        for tweet in data.get("statuses", []):
            text = tweet.get("full_text") or tweet.get("text", "")

            # Remove URLs
            import re
            text = re.sub(r"https?://\S+", "", text).strip()

            if len(text) < 30:
                continue

            # Check for prompt-like content
            has_prompt_kw = any(kw in text.lower() for kw in [
                "prompt", "提示词", "generate", "image of", "photo",
                "photography", "product", "ecommerce", "电商"
            ])
            if not has_prompt_kw:
                continue

            media = tweet.get("entities", {}).get("media", [])
            images = [m["media_url_https"] for m in media if m.get("type") == "photo"][:4]

            retweets = tweet.get("retweet_count", 0)
            favorites = tweet.get("favorite_count", 0)
            trend = min(100, max(10, (retweets + favorites) / 10))

            items.append({
                "title": text[:60].replace("\n", " "),
                "content": text,
                "category": self._guess_category(text),
                "scenario": "日常种草",
                "platform": "通用",
                "output_type": "主图提示词",
                "preview_images": images,
                "trend_score": trend,
            })

            if len(items) >= 15:
                break

        return self.save_to_db(items)

    def _guess_category(self, text: str) -> str:
        t = text.lower()
        for kw, cat in [
            ("dress", "服饰"), ("fashion", "服饰"), ("cloth", "服饰"),
            ("makeup", "美妆"), ("skincare", "美妆"), ("cosmetic", "美妆"),
            ("phone", "3C数码"), ("laptop", "3C数码"), ("electronic", "3C数码"),
            ("food", "食品"), ("cake", "食品"), ("drink", "食品"),
            ("furniture", "家居"), ("interior", "家居"), ("home", "家居"),
            ("baby", "母婴"), ("toy", "母婴"),
            ("sport", "运动户外"), ("outdoor", "运动户外"), ("fitness", "运动户外"),
            ("jewelry", "珠宝饰品"), ("necklace", "珠宝饰品"),
        ]:
            if kw in t:
                return cat
        return "其他"

    def _fallback(self) -> int:
        seeds = [
            {
                "title": "GPT Image 2 电商产品摄影提示词",
                "category": "服饰", "scenario": "新品推广", "platform": "通用",
                "output_type": "主图提示词", "trend_score": 88,
                "preview_images": ["https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&h=400&fit=crop"],
                "content": "Create a professional e-commerce product photo using GPT Image 2: A minimalist stainless steel water bottle, studio lighting with soft shadows, white background, 3/4 angle view, lifestyle context with a yoga mat and towel in the blurred background, product sharp and in focus, commercial photography style, 1:1 square format, suitable for Amazon product listing main image"
            },
            {
                "title": "AI 电商主图 — 服装拍摄",
                "category": "服饰", "scenario": "日常种草", "platform": "淘宝",
                "output_type": "主图提示词", "trend_score": 86,
                "preview_images": ["https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&h=400&fit=crop"],
                "content": "E-commerce fashion photography, casual summer dress on mannequin, natural sunlight through window, soft warm tones, fabric texture visible, front and back view, 8K resolution, professional catalog style, suitable for online store product page"
            },
            {
                "title": "AI 产品摄影 — 化妆品拍摄",
                "category": "美妆", "scenario": "大促促销", "platform": "天猫",
                "output_type": "主图提示词", "trend_score": 84,
                "preview_images": ["https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&h=400&fit=crop"],
                "content": "Professional cosmetic product photography, luxury serum bottle with dropper, rose gold cap, gradient pink background, water droplets on glass surface, soft diffused lighting, macro detail shot, premium beauty branding style, 8K resolution"
            },
            {
                "title": "GPT Image 产品系列图模板",
                "category": "3C数码", "scenario": "新品推广", "platform": "通用",
                "output_type": "主图提示词", "trend_score": 82,
                "preview_images": ["https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=600&h=400&fit=crop"],
                "content": "Generate a series of 3 consistent product images for a premium wireless keyboard: 1) Hero shot - product on dark desk with dramatic side lighting 2) Detail close-up - mechanical key switches and aluminum frame texture 3) Lifestyle - modern minimalist office setup with the keyboard as focal point. All images must maintain consistent color temperature, lighting style, and product appearance."
            },
            {
                "title": "AI 电商图 — 食品产品摄影",
                "category": "食品", "scenario": "日常种草", "platform": "小红书",
                "output_type": "主图提示词", "trend_score": 80,
                "preview_images": ["https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=600&h=400&fit=crop"],
                "content": "Flat lay food photography, artisanal chocolate collection arranged on marble surface, cocoa powder dusting, gold foil accents, natural window light from left, shallow depth of field focusing on front piece, warm rich tones, premium food branding style, suitable for social media product promotion"
            },
        ]
        return self.save_to_db(seeds)
