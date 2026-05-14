"""GPT Image 2 提示词爬虫 — 从 EvoLinkAI/awesome-gpt-image-2-API-and-Prompts 抓取全部提示词"""
import re
from .base import BaseCrawler

class GptImage2Crawler(BaseCrawler):
    name = "gptimage2"

    RAW_BASE = "https://raw.githubusercontent.com/EvoLinkAI/awesome-gpt-image-2-API-and-Prompts/main"

    CATEGORY_FILES = {
        "portrait":    "portrait",
        "ui":          "ui",
        "comparison":  "comparison",
        "ecommerce":   "ecommerce",
        "poster":      "poster",
        "ad-creative": "ad-creative",
        "character":   "character",
    }

    CATEGORY_MAP = {
        "portrait":    "服饰",
        "ui":          "3C数码",
        "comparison":  "3C数码",
        "ecommerce":   "其他",
        "poster":      "其他",
        "ad-creative": "其他",
        "character":   "其他",
    }

    ECOM_KEYWORDS = {
        "服饰": ["服装", "衣服", "裙子", "外套", "鞋", "帽子", "包包", "手表", "首饰", "围巾", "眼镜",
                 "dress", "jacket", "shoes", "bag", "watch", "jewelry", "fashion", "clothing", "outfit", "coat",
                 "sweater", "shirt", "pants", "boots", "sneakers", "necklace", "earrings"],
        "美妆": ["口红", "香水", "面膜", "护肤", "化妆", "美妆", "粉底", "眼影", "腮红",
                 "lipstick", "perfume", "skincare", "makeup", "cosmetic", "foundation", "eyeshadow"],
        "3C数码": ["手机", "电脑", "耳机", "相机", "手表", "平板", "键盘", "鼠标", "音箱",
                   "phone", "laptop", "headphone", "camera", "tablet", "keyboard", "speaker", "tech", "device"],
        "食品": ["食物", "美食", "饮料", "咖啡", "茶", "巧克力", "甜点", "水果", "零食",
                 "food", "drink", "coffee", "tea", "chocolate", "dessert", "fruit", "snack", "cake"],
        "家居": ["家具", "沙发", "床", "桌子", "椅子", "灯具", "花瓶", "地毯", "窗帘",
                 "furniture", "sofa", "bed", "table", "chair", "lamp", "vase", "carpet", "home", "interior"],
        "母婴": ["婴儿", "儿童", "玩具", "童装", "奶瓶", "尿布",
                 "baby", "kids", "toy", "children", "infant", "stroller"],
        "运动户外": ["运动", "跑步", "健身", "瑜伽", "登山", "露营", "游泳", "篮球", "足球",
                     "sports", "running", "fitness", "yoga", "hiking", "camping", "swimming", "basketball"],
        "珠宝饰品": ["珠宝", "钻石", "黄金", "戒指", "项链", "手链", "耳环",
                     "diamond", "gold", "ring", "bracelet", "jewelry", "pendant"],
    }

    def _guess_category(self, title, content):
        """关键词匹配覆盖类别"""
        text = (title + " " + content).lower()
        for cat, keywords in self.ECOM_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text:
                    return cat
        return None

    def _extract_image_url(self, block, github_category, case_num):
        """从 case block 中提取图片 URL"""
        # 匹配 <img src="..."> — 可能是绝对 URL 或相对路径
        m = re.search(r'<img[^>]*src="([^"]*)"[^>]*>', block)
        if m:
            url = m.group(1)
            if url.startswith("http"):
                return url
            # 相对路径，如 ../images/portrait_case1/output.jpg
            # 去掉 ../ 并补全
            url = url.replace("../", "")
            return f"{self.RAW_BASE}/{url}"
        return ""

    def _extract_prompts(self, block):
        """提取所有提示词文本，返回列表"""
        prompts = []

        # 找到所有 **Prompt...:** 的位置
        prompt_headers = list(re.finditer(
            r'\*\*Prompt\s*(?:\d+)?(?:\s*\([^)]*\))?\s*:?\*\*\s*:?\s*',
            block
        ))

        if not prompt_headers:
            return prompts

        for i, header_match in enumerate(prompt_headers):
            start = header_match.end()
            # 下一个 ** 标题、### Case、或 **Output**、**Source**
            end = len(block)
            if i + 1 < len(prompt_headers):
                end = prompt_headers[i + 1].start()
            else:
                # 找下一个 section 标记
                for pattern in [r'\*\*Output', r'\*\*Source', r'### Case', r'---\s*\n']:
                    m = re.search(pattern, block[start:])
                    if m:
                        end = start + m.start()
                        break

            section = block[start:end].strip()

            # 提取代码块内容
            code_match = re.search(r'```(?:\w+)?\s*\n(.*?)```', section, re.DOTALL)
            if code_match:
                prompt_text = code_match.group(1).strip()
            else:
                # 无代码块，直接取文本
                prompt_text = section.strip()

            # 跳过太短的
            if prompt_text and len(prompt_text) >= 30:
                prompts.append(prompt_text)

        return prompts

    def _parse_standard_case(self, block, github_category):
        """Format A: 标题含 [Title](url) (by [@author])，表格图片"""
        items = []

        # 提取标题和 tweet URL
        title_match = re.search(r'### Case \d+:\s*\[([^\]]+)\]\(([^)]+)\)', block)
        if not title_match:
            # 尝试匹配无 URL 的标题
            title_match = re.search(r'### Case \d+:\s*(.+?)(?:\n|$)', block)
            title = title_match.group(1).strip() if title_match else "Untitled"
            tweet_url = ""
        else:
            title = title_match.group(1).strip()
            tweet_url = title_match.group(2)

        # 提取作者
        author_match = re.search(r'\(by \[(@?\w+)\]\(([^)]*)\)\)', block)
        author = author_match.group(1) if author_match else ""

        # 提取 case number
        case_num_match = re.search(r'### Case (\d+):', block)
        case_num = int(case_num_match.group(1)) if case_num_match else 0

        # 提取图片
        image_url = self._extract_image_url(block, github_category, case_num)

        # 提取提示词
        prompt_texts = self._extract_prompts(block)

        if not prompt_texts:
            return items

        for i, prompt_text in enumerate(prompt_texts):
            t = title
            if len(prompt_texts) > 1:
                t = f"{title} (Prompt {i+1})"

            category = self._guess_category(t, prompt_text) or self.CATEGORY_MAP.get(github_category, "其他")
            items.append({
                "title": t[:120],
                "content": prompt_text,
                "category": category,
                "scenario": "日常种草",
                "platform": f"GPT-Image-2{f' (@{author})' if author else ''}",
                "output_type": "主图提示词",
                "preview_images": [image_url] if image_url else [],
                "trend_score": min(100, 50 + (15 if case_num >= 200 else 10 if case_num >= 100 else 5 if case_num >= 50 else 0) + (5 if github_category in ("poster", "portrait") else 0)),
            })

        return items

    def _parse_source_case(self, block, github_category):
        """Format B: **Source:** 字段，无 tweet URL"""
        items = []

        # 标题
        title_match = re.search(r'### Case \d+:\s*(.+?)(?:\n|$)', block)
        title = title_match.group(1).strip() if title_match else "Untitled"

        case_num_match = re.search(r'### Case (\d+):', block)
        case_num = int(case_num_match.group(1)) if case_num_match else 0

        # 作者
        author_match = re.search(r'\*\*Source\*\*:\s*\[(@?\w+)\]\(([^)]*)\)', block)
        author = author_match.group(1) if author_match else ""

        # 图片 — Source 格式中 img 在 **Output:** 后面
        output_section = re.search(r'\*\*Output\*\*:?\s*\n(.*?)(?:\*\*|### Case|---\s*\n|$)', block, re.DOTALL)
        output_block = output_section.group(1) if output_section else block
        image_url = self._extract_image_url(output_block, github_category, case_num)

        # 提示词
        prompt_texts = self._extract_prompts(block)

        if not prompt_texts:
            return items

        for i, prompt_text in enumerate(prompt_texts):
            t = title
            if len(prompt_texts) > 1:
                t = f"{title} (Prompt {i+1})"

            category = self._guess_category(t, prompt_text) or self.CATEGORY_MAP.get(github_category, "其他")
            items.append({
                "title": t[:120],
                "content": prompt_text,
                "category": category,
                "scenario": "日常种草",
                "platform": f"GPT-Image-2{f' (@{author})' if author else ''}",
                "output_type": "主图提示词",
                "preview_images": [image_url] if image_url else [],
                "trend_score": min(100, 50 + (15 if case_num >= 200 else 10 if case_num >= 100 else 5 if case_num >= 50 else 0) + (5 if github_category in ("poster", "portrait") else 0)),
            })

        return items

    def _detect_format(self, block):
        """检测 case 格式：A = 标准（有 tweet URL），B = Source 格式"""
        if "**Source**:" in block and "**Prompt**" in block and "**Output**" in block:
            return "B"
        return "A"

    def _fetch_and_parse_file(self, github_category):
        """下载一个类别的 markdown 文件并解析所有 case"""
        url = f"{self.RAW_BASE}/cases/{github_category}.md"
        print(f"[gptimage2] Fetching {url}")
        try:
            text = self.fetch(url)
        except Exception as e:
            print(f"[gptimage2] Failed to fetch {github_category}: {e}")
            return []

        items = []
        # 按 ### Case 拆分
        parts = re.split(r'(?=### Case \d+)', text)

        for part in parts:
            if not part.startswith("### Case "):
                continue

            fmt = self._detect_format(part)
            try:
                if fmt == "A":
                    items += self._parse_standard_case(part, github_category)
                else:
                    items += self._parse_source_case(part, github_category)
            except Exception as e:
                case_info = part[:80].replace("\n", " ")
                print(f"[gptimage2] Error parsing {case_info}...: {e}")
                continue

        return items

    def run(self):
        """主入口 — 抓取所有 7 个文件并保存"""
        all_items = []
        for github_category in self.CATEGORY_FILES:
            items = self._fetch_and_parse_file(github_category)
            print(f"[gptimage2] {github_category}: {len(items)} prompts parsed")
            all_items += items

        if not all_items:
            print("[gptimage2] No items parsed, skipping save")
            return 0

        count = self.save_to_db(all_items)
        print(f"[gptimage2] Saved {count} new prompts (total {len(all_items)} parsed)")
        return count
