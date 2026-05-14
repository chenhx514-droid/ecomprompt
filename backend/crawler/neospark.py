"""NeoSpark GPT Image 2 提示词爬虫 — 从 useneospark/awesome-gpt-image-2 抓取全部提示词"""
import re
import os
import json
import gzip
from .base import BaseCrawler

class NeoSparkCrawler(BaseCrawler):
    name = "neospark"

    RAW_BASE = "https://raw.githubusercontent.com/useneospark/awesome-gpt-image-2/main"

    CATEGORIES = [
        "product",
        "portraits",
        "cinematic",
        "fantasy",
        "nature",
        "architecture",
        "ui-design",
        "typography",
        "marketing",
        "experimental",
        "featured",
    ]

    CATEGORY_MAP = {
        "product":      "其他",
        "portraits":    "服饰",
        "cinematic":    "其他",
        "fantasy":      "其他",
        "nature":       "其他",
        "architecture": "家居",
        "ui-design":    "3C数码",
        "typography":   "其他",
        "marketing":    "其他",
        "experimental": "其他",
        "featured":     "其他",
    }

    ECOM_KEYWORDS = {
        "服饰": ["服装", "衣服", "裙子", "外套", "鞋", "帽子", "包包", "手表", "首饰", "围巾", "眼镜",
                 "dress", "jacket", "shoes", "bag", "watch", "jewelry", "fashion", "clothing", "outfit", "coat",
                 "sweater", "shirt", "pants", "boots", "sneakers", "necklace", "earrings", "leather", "silk"],
        "美妆": ["口红", "香水", "面膜", "护肤", "化妆", "美妆", "粉底", "眼影", "腮红",
                 "lipstick", "perfume", "skincare", "makeup", "cosmetic", "foundation", "eyeshadow", "beauty"],
        "3C数码": ["手机", "电脑", "耳机", "相机", "手表", "平板", "键盘", "鼠标", "音箱",
                   "phone", "laptop", "headphone", "camera", "tablet", "keyboard", "speaker", "tech", "device",
                   "earbuds", "wireless", "mechanical keyboard", "rgb", "gaming"],
        "食品": ["食物", "美食", "饮料", "咖啡", "茶", "巧克力", "甜点", "水果", "零食",
                 "food", "drink", "coffee", "tea", "chocolate", "dessert", "fruit", "snack", "cake", "bottle"],
        "家居": ["家具", "沙发", "床", "桌子", "椅子", "灯具", "花瓶", "地毯", "窗帘",
                 "furniture", "sofa", "bed", "table", "chair", "lamp", "vase", "carpet", "home", "interior",
                 "kettle", "kitchen", "marble", "wooden", "oak", "walnut", "ceramic"],
        "母婴": ["婴儿", "儿童", "玩具", "童装", "奶瓶", "尿布",
                 "baby", "kids", "toy", "children", "infant", "stroller"],
        "运动户外": ["运动", "跑步", "健身", "瑜伽", "登山", "露营", "游泳", "篮球", "足球",
                     "sports", "running", "fitness", "yoga", "hiking", "camping", "swimming", "basketball",
                     "sneaker", "trainer"],
        "珠宝饰品": ["珠宝", "钻石", "黄金", "戒指", "项链", "手链", "耳环",
                     "diamond", "gold", "ring", "bracelet", "jewelry", "pendant", "luxury"],
    }

    def _guess_category(self, title, content):
        text = (title + " " + content).lower()
        for cat, keywords in self.ECOM_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text:
                    return cat
        return None

    def _title_to_slug(self, title):
        """标题转文件名 slug: 'Coffee Bag Packaging' -> 'coffee-bag-packaging'"""
        slug = title.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    def _parse_prompts(self, text):
        """解析 markdown: 每个 ### Title 后紧跟 > prompt 引用块"""
        items = []
        # 按 ### 标题分割
        sections = re.split(r'\n### ', text)

        for section in sections:
            # 提取标题（第一行）
            lines = section.strip().split('\n')
            title = lines[0].strip()
            # 跳过非标题行（文件头部等）
            if not title or title.startswith('#') or title.startswith('>'):
                continue

            # 合并 prompt 文本 — > 开头的引用行
            prompt_lines = []
            for line in lines[1:]:
                stripped = line.strip()
                if stripped.startswith('> '):
                    prompt_lines.append(stripped[2:])
                elif stripped.startswith('>'):
                    prompt_lines.append(stripped[1:])
                elif stripped.startswith('##') or stripped.startswith('---'):
                    break  # 下一个 section

            prompt_text = ' '.join(prompt_lines).strip()
            if not prompt_text or len(prompt_text) < 30:
                continue

            items.append({"title": title, "content": prompt_text})

        return items

    def _fetch_and_parse_category(self, category):
        """下载一个类别的 README 并解析"""
        url = f"{self.RAW_BASE}/prompts/{category}/README.md"
        print(f"[neospark] Fetching {url}")
        try:
            import httpx
            with httpx.Client(timeout=60) as client:
                resp = client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; EcomPrompt/1.0)"
                })
                resp.raise_for_status()
                text = resp.text
        except Exception as e:
            print(f"[neospark] Failed to fetch {category}: {e}")
            return []

        raw_items = self._parse_prompts(text)
        items = []
        for ri in raw_items:
            title = ri["title"]
            content = ri["content"]
            slug = self._title_to_slug(title)
            image_url = f"{self.RAW_BASE}/public/images/{category}/{slug}.png"

            category_ecom = self._guess_category(title, content) or self.CATEGORY_MAP.get(category, "其他")

            items.append({
                "title": title[:120],
                "content": content,
                "category": category_ecom,
                "scenario": "日常种草",
                "platform": f"GPT-Image-2 (NeoSpark/{category})",
                "output_type": "主图提示词",
                "preview_images": [image_url],
                "trend_score": 60,
            })

        return items

    def _load_seed(self):
        """从种子文件加载"""
        seed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neospark_seed.json.gz")
        if os.path.exists(seed_path):
            with gzip.open(seed_path, "rt", encoding="utf-8") as f:
                return json.load(f)
        return []

    def run(self):
        """主入口"""
        all_items = []
        for category in self.CATEGORIES:
            try:
                items = self._fetch_and_parse_category(category)
                print(f"[neospark] {category}: {len(items)} prompts parsed")
                all_items += items
            except Exception as e:
                print(f"[neospark] Error processing {category}: {e}")

        if not all_items:
            print("[neospark] Live fetch produced 0 items, loading seed data...")
            all_items = self._load_seed()

        if not all_items:
            print("[neospark] No items, skipping save")
            return 0

        count = self.save_to_db(all_items)
        print(f"[neospark] Saved {count} new prompts (total {len(all_items)} parsed)")
        return count
