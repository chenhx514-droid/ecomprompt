"""YouMind 爬虫 — 从 awesome-gpt-image-2 GitHub 仓库提取电商相关提示词"""
import re
from .base import BaseCrawler

README_URL = "https://raw.githubusercontent.com/YouMind-OpenLab/awesome-gpt-image-2/main/README_zh.md"


class YoumindCrawler(BaseCrawler):
    name = "youmind"

    ECOM_KEYWORDS = [
        "电商", "主图", "产品", "商品", "淘宝", "天猫", "亚马逊", "拼多多",
        "ecommerce", "e-commerce", "product photo", "product shot",
        "product marketing", "shopping", "retail",
        "fashion", "clothing", "dress", "apparel",
        "cosmetic", "makeup", "skincare",
        "furniture", "food photo",
    ]

    def run(self) -> int:
        try:
            text = self.fetch(README_URL)
            if not text or len(text) < 1000:
                print("[youmind] README fetch failed, using fallback")
                return self._fallback()

            prompts = self._parse_readme(text)
            if not prompts:
                print("[youmind] No ecommerce prompts found, using fallback")
                return self._fallback()

            return self.save_to_db(prompts)

        except Exception as e:
            print(f"[youmind] Error: {e}")
            return self._fallback()

    def _parse_readme(self, text: str) -> list:
        # Split into prompt sections (each starts with "### No. X:")
        sections = re.split(r"\n(?=### No\. \d+:)", text)
        items = []

        for section in sections:
            title_match = re.search(r"### No\. \d+:\s*(.+?)(?:\n|$)", section)
            if not title_match:
                continue
            title = title_match.group(1).strip()

            # Check if ecommerce-related
            combined = (title + " " + section[:500]).lower()
            if not any(kw in combined for kw in self.ECOM_KEYWORDS):
                continue

            # Extract prompt content
            content = self._extract_content(section)
            if not content or len(content) < 20:
                continue

            # Extract images
            images = re.findall(r'<img src="(https://cms-assets\.youmind\.com/[^"]+)"', section)
            images = list(dict.fromkeys(images))[:4]

            # Extract category from description
            category = self._guess_category(title + " " + section[:1000])

            # Extract description
            desc_match = re.search(r"#### 📖 .*?\n\n(.+?)\n\n", section)
            desc = desc_match.group(1).strip() if desc_match else title

            items.append({
                "title": title[:60],
                "content": content,
                "category": category,
                "scenario": "新品推广",
                "platform": "通用",
                "output_type": "主图提示词",
                "preview_images": images,
                "trend_score": 75,
            })

            if len(items) >= 30:
                break

        return items

    def _extract_content(self, section: str) -> str:
        # Try to extract from code block after "#### 📝 提示词"
        code_match = re.search(
            r"#### 📝 (?:提示词|Prompt|).*?\n```(?:json)?\s*\n(.+?)\n```",
            section, re.DOTALL
        )
        if code_match:
            return code_match.group(1).strip()

        # Try generic code block
        code_match = re.search(r"```(?:json)?\s*\n(.+?)\n```", section, re.DOTALL)
        if code_match:
            content = code_match.group(1).strip()
            if len(content) > 30:
                return content

        # Try extracting between #### 📝 and next ####
        desc_match = re.search(r"#### 📝 .*?\n\n(.+?)\n\n####", section, re.DOTALL)
        if desc_match:
            content = desc_match.group(1).strip()
            if len(content) > 20 and len(content) < 3000:
                return content

        return ""

    def _guess_category(self, text: str) -> str:
        text = text.lower()
        for kw, cat in [
            ("服饰", "服饰"), ("dress", "服饰"), ("fashion", "服饰"), ("clothing", "服饰"),
            ("美妆", "美妆"), ("makeup", "美妆"), ("skincare", "美妆"), ("cosmetic", "美妆"),
            ("数码", "3C数码"), ("phone", "3C数码"), ("laptop", "3C数码"),
            ("食品", "食品"), ("food", "食品"), ("零食", "食品"),
            ("家居", "家居"), ("furniture", "家居"), ("interior", "家居"),
            ("母婴", "母婴"), ("baby", "母婴"),
            ("运动", "运动户外"), ("sport", "运动户外"), ("fitness", "运动户外"),
            ("珠宝", "珠宝饰品"), ("jewelry", "珠宝饰品"), ("necklace", "珠宝饰品"),
        ]:
            if kw in text:
                return cat
        return "其他"

    def _fallback(self) -> int:
        seeds = [
            {
                "title": "电商主图 — 白底产品摄影",
                "category": "服饰", "scenario": "新品推广", "platform": "淘宝",
                "output_type": "主图提示词", "trend_score": 92,
                "preview_images": ["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&h=400&fit=crop"],
                "content": "E-commerce product photography, white background, studio lighting, professional product shot, 8K resolution, clean composition, product centered, 1:1 aspect ratio, soft shadows, commercial photography style"
            },
            {
                "title": "电商主图 — 美妆产品场景图",
                "category": "美妆", "scenario": "大促促销", "platform": "天猫",
                "output_type": "主图提示词", "trend_score": 88,
                "preview_images": ["https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&h=400&fit=crop"],
                "content": "Luxury skincare product photography, marble background, natural sunlight, water droplets, rose gold accents, premium cosmetic branding, clean elegant composition, 8K resolution, commercial beauty photography"
            },
            {
                "title": "电商主图 — 数码产品拍摄",
                "category": "3C数码", "scenario": "新品推广", "platform": "通用",
                "output_type": "主图提示词", "trend_score": 85,
                "preview_images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop"],
                "content": "Product photography of wireless earbuds, sleek modern design, dramatic lighting, reflection on black acrylic surface, professional commercial photography, studio lighting setup, 8K ultra HD, minimal composition"
            },
            {
                "title": "电商营销 — 618大促海报",
                "category": "美妆", "scenario": "大促促销", "platform": "天猫",
                "output_type": "主图提示词", "trend_score": 90,
                "preview_images": ["https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&h=400&fit=crop"],
                "content": "618 shopping festival promotional poster, luxury cosmetics gift set, festive red and gold color scheme, confetti effects, premium gift packaging, celebration atmosphere, commercial advertising style, Chinese e-commerce promotion"
            },
            {
                "title": "电商产品 — 食品饮料拍摄",
                "category": "食品", "scenario": "日常种草", "platform": "小红书",
                "output_type": "主图提示词", "trend_score": 82,
                "preview_images": ["https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600&h=400&fit=crop"],
                "content": "Artisan bakery product photography, freshly baked pastries, golden morning light, rustic wooden table, crumbs and flour dust details, cozy bakery atmosphere, warm tones, shallow depth of field, 8K resolution, commercial food photography"
            },
            {
                "title": "电商产品 — 珠宝首饰展示",
                "category": "珠宝饰品", "scenario": "新品推广", "platform": "通用",
                "output_type": "主图提示词", "trend_score": 80,
                "preview_images": ["https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&h=400&fit=crop"],
                "content": "Jewelry product photography, diamond necklace on black velvet, dramatic spotlight, sparkle and brilliance capture, macro lens, luxury jewelry advertising style, 8K ultra HD, clean elegant composition"
            },
        ]
        return self.save_to_db(seeds)
