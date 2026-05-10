"""GitHub 爬虫 — 搜索 ChatGPT-Image / GPT-4o 相关的电商提示词仓库 + 提取预览图"""
from .base import BaseCrawler
import urllib.parse
import json
import re

class GitHubCrawler(BaseCrawler):
    name = "github"

    # ChatGPT-Image 相关的搜索主题
    TOPICS = [
        "chatgpt-image",
        "gpt-image-1",
        "chatgpt-image-generation",
        "chatgpt-4o-image",
    ]

    # 知名 ChatGPT-Image 提示词仓库（直接拉取）
    KNOWN_REPOS = [
        {
            "owner": "deepseek-ai",
            "repo": "awesome-deepseek-integration",
            "files": [],
            "category": "3C数码",
        },
        {
            "owner": "linexjlin",
            "repo": "GPTS",
            "files": [],
            "category": "通用",
        },
    ]

    # 搜索关键词
    QUERIES = [
        "chatgpt image generation prompt ecommerce",
        "chatgpt image product photography prompt",
        "gpt-image prompt collection",
        'chatgpt 4o image 电商 prompt',
        "chatgpt-image prompt template",
    ]

    def run(self) -> int:
        total = 0

        # 1. 搜索 GitHub code 找到包含 ChatGPT-image prompt 的文件
        for query in self.QUERIES[:2]:
            try:
                count = self._search_and_fetch(query)
                total += count
            except Exception as e:
                print(f"[github] search failed: {e}")

        # 2. 搜索 repos
        for topic in self.TOPICS[:2]:
            try:
                count = self._search_repos(topic)
                total += count
            except Exception as e:
                print(f"[github] topic '{topic}' failed: {e}")

        return total

    def _search_and_fetch(self, query: str) -> int:
        """搜索代码并尝试拉取原始内容"""
        q = f"{query} language:markdown"
        url = f"https://api.github.com/search/code?q={urllib.parse.quote(q)}&per_page=15"
        data = self.fetch_json(url)
        items = []

        for item in data.get("items", []):
            repo_full = item.get("repository", {}).get("full_name", "")
            path = item.get("path", "")
            html_url = item.get("html_url", "")
            if not repo_full or not path:
                continue

            # 尝试从 raw URL 获取真实内容
            content = self._fetch_raw_content(repo_full, path)
            if not content:
                # 回退：只提供链接
                content = f"View prompts at: {html_url}"

            # 提取文件中引用的图片
            images = self._extract_images(content, repo_full, path)

            # 从内容中提取提示词片段
            prompts = self._extract_prompts(content)
            if prompts:
                for prompt_text in prompts[:3]:
                    title = path.replace(".md", "").replace(".json", "").replace("-", " ").replace("_", " ")[:60]
                    category = self._guess_category(title + " " + prompt_text)
                    items.append({
                        "title": title,
                        "content": prompt_text,
                        "category": category,
                        "scenario": "日常种草",
                        "platform": "通用",
                        "output_type": "主图提示词",
                        "trend_score": 60 + (10 if images else 0),
                        "preview_images": images[:4],
                    })
            else:
                title = path.replace(".md", "").replace(".json", "").replace("-", " ").replace("_", " ")[:60]
                items.append({
                    "title": title,
                    "content": content,
                    "category": self._guess_category(title),
                    "scenario": "日常种草",
                    "platform": "通用",
                    "output_type": "主图提示词",
                    "trend_score": 45,
                    "preview_images": images[:4],
                })

        return self.save_to_db(items)

    def _search_repos(self, topic: str) -> int:
        """搜索带有特定 topic 的仓库"""
        url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(topic)}+in:topic&sort=stars&per_page=10"
        data = self.fetch_json(url)
        items = []

        for repo in data.get("items", []):
            full_name = repo.get("full_name", "")
            description = repo.get("description", "") or ""
            stars = repo.get("stargazers_count", 0)
            url = repo.get("html_url", "")

            if not full_name or stars < 10:
                continue

            items.append({
                "title": f"{full_name} - ChatGPT Image Prompts",
                "content": f"GitHub: {url}\nDescription: {description}\nStars: {stars}\n\nThis repository contains ChatGPT-Image generation prompts and examples. Browse the repo for specific prompt files.",
                "category": self._guess_category(description.lower()),
                "scenario": "日常种草",
                "platform": "通用",
                "output_type": "主图提示词",
                "trend_score": min(100, max(30, stars / 50)),
                "preview_images": [],
            })

        return self.save_to_db(items)

    def _fetch_raw_content(self, repo_full: str, path: str) -> str:
        """从 raw.githubusercontent.com 拉取文件内容"""
        import httpx
        # 尝试 main 和 master 分支
        for branch in ["main", "master"]:
            raw_url = f"https://raw.githubusercontent.com/{repo_full}/{branch}/{path}"
            try:
                with httpx.Client(timeout=10) as client:
                    resp = client.get(raw_url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    })
                    if resp.status_code == 200:
                        text = resp.text
                        if len(text) > 10000:
                            text = text[:10000]
                        return text
            except Exception:
                continue
        return ""

    def _extract_prompts(self, content: str) -> list:
        """从 markdown 或 JSON 文件中提取提示词文本"""
        if not content or len(content) < 20:
            return []

        prompts = []

        # 尝试 JSON 格式
        try:
            data = json.loads(content)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        prompt = item.get("prompt") or item.get("text") or item.get("content", "")
                        if prompt and len(prompt) > 20:
                            prompts.append(prompt)
                    elif isinstance(item, str) and len(item) > 20:
                        prompts.append(item)
            elif isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, str) and len(v) > 20:
                        prompts.append(v)
            if prompts:
                return prompts
        except (json.JSONDecodeError, TypeError):
            pass

        # Markdown 格式：提取代码块和引用的段落
        import re
        # 提取 markdown 代码块
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        for block in code_blocks:
            clean = block.strip('`').strip()
            # 去掉语言标记
            if '\n' in clean:
                first_line, rest = clean.split('\n', 1)
                if len(first_line) < 20 and not ' ' in first_line:
                    clean = rest
            clean = clean.strip()
            if len(clean) > 30 and len(clean) < 2000:
                prompts.append(clean)

        # 提取引用的段落 (> 开头)
        quotes = re.findall(r'^> (.{30,500})$', content, re.MULTILINE)
        prompts.extend(quotes[:5])

        # 提取长的连续行（可能包含完整prompt）
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 60 and len(line) < 2000 and not line.startswith('#') and not line.startswith('!'):
                # 包含关键词
                if any(kw in line.lower() for kw in [
                    'prompt:', 'prompt：', 'image of', 'photo of', 'photograph',
                    'e-commerce', 'ecommerce', 'product', 'generate',
                    '提示词', '生成', '电商', '摄影'
                ]):
                    prompts.append(line)

        return prompts[:10]  # 最多10条

    def _extract_images(self, content: str, repo_full: str, file_path: str) -> list:
        """从 markdown/JSON 内容中提取图片 URL，转换相对路径为绝对路径"""
        images = []

        # 1. Markdown 图片语法: ![alt](url)
        md_images = re.findall(r'!\[.*?\]\((https?://[^\s)]+)\)', content)
        images.extend(md_images)

        # 2. 相对路径图片: ![alt](./images/xxx.png)
        rel_images = re.findall(r'!\[.*?\]\(\./([^\s)]+\.(?:png|jpg|jpeg|gif|webp))\)', content, re.IGNORECASE)
        rel_images += re.findall(r'!\[.*?\]\(([^\s)]+\.(?:png|jpg|jpeg|gif|webp))\)', content, re.IGNORECASE)

        for rel_path in rel_images:
            if rel_path.startswith("http"):
                images.append(rel_path)
                continue
            # 转换相对路径为 GitHub raw URL
            dir_path = "/".join(file_path.split("/")[:-1])
            if rel_path.startswith("/"):
                full_path = rel_path.lstrip("/")
            else:
                full_path = f"{dir_path}/{rel_path}"
            raw_url = f"https://raw.githubusercontent.com/{repo_full}/main/{full_path}"
            images.append(raw_url)

        # 3. HTML img 标签
        html_images = re.findall(r'<img[^>]+src="([^"]+)"', content)
        for img in html_images:
            if img.startswith("http"):
                images.append(img)

        # 4. 直接的行内图片链接
        inline = re.findall(r'(https?://[^\s]+\.(?:png|jpg|jpeg|gif|webp)[^\s]*)', content, re.IGNORECASE)
        images.extend(inline)

        # 5. Unsplash / placeholder 等常用图床链接
        cdn_patterns = [
            r'https?://images\.unsplash\.com/[^\s)]+',
            r'https?://[^\s)]+\.cloudfront\.net/[^\s)]+',
            r'https?://[^\s)]+\.githubusercontent\.com/[^\s)]+',
        ]
        for pat in cdn_patterns:
            images.extend(re.findall(pat, content))

        # 去重 + 过滤 + 限制
        seen = set()
        result = []
        for url in images:
            url = url.rstrip(")").rstrip(",").rstrip(".")
            if url in seen:
                continue
            seen.add(url)
            # 跳过太小/明显不是图片的 URL
            if any(skip in url.lower() for skip in [".svg", "badge", "shield", "avatar", "icon"]):
                continue
            result.append(url)
            if len(result) >= 6:
                break

        return result

    def _guess_category(self, text: str) -> str:
        text = text.lower()
        for kw, cat in [
            ("服", "服饰"), ("dress", "服饰"), ("cloth", "服饰"), ("fashion", "服饰"), ("汉服", "服饰"), ("旗袍", "服饰"),
            ("美妆", "美妆"), ("妆", "美妆"), ("makeup", "美妆"), ("cosmetic", "美妆"), ("口红", "美妆"),
            ("数码", "3C数码"), ("手机", "3C数码"), ("耳机", "3C数码"), ("phone", "3C数码"), ("laptop", "3C数码"),
            ("食品", "食品"), ("food", "食品"), ("零食", "食品"), ("cake", "食品"),
            ("家居", "家居"), ("home", "家居"), ("家具", "家居"), ("furniture", "家居"), ("interior", "家居"),
            ("母婴", "母婴"), ("baby", "母婴"), ("孕", "母婴"), ("toy", "母婴"),
            ("运动", "运动户外"), ("sport", "运动户外"), ("户外", "运动户外"), ("fitness", "运动户外"),
            ("首饰", "珠宝饰品"), ("珠宝", "珠宝饰品"), ("jewel", "珠宝饰品"), ("necklace", "珠宝饰品"),
        ]:
            if kw in text:
                return cat
        return "其他"
