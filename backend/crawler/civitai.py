from .base import BaseCrawler

class CivitaiCrawler(BaseCrawler):
    """抓取 Civitai 公开API - AI图像及其提示词。

    Civitai 是最大的 Stable Diffusion 模型/图像分享社区。
    每个图像都包含生成时的完整 prompt，天然附带效果图。
    公开 API 无需认证即可访问。
    """

    name = "civitai"
    API_URL = "https://civitai.com/api/v1/images"

    # 电商相关的标签筛选
    ECOM_TAGS = [
        "product", "ecommerce", "fashion", "clothing", "dress",
        "cosmetics", "skincare", "jewelry", "food photography",
        "interior design", "furniture", "sports gear", "electronics",
        "product photography", "commercial", "packshot"
    ]

    def run(self) -> int:
        try:
            # 拉取最新热门图像，带商业/产品相关标签
            params = {
                "limit": 50,
                "sort": "Most Reactions",
                "period": "Week",
                "nsfw": "None",
            }
            url = f"{self.API_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
            data = self.fetch_json(url)

            items = []
            for img in data.get("items", []):
                meta = img.get("meta", {})
                prompt_text = meta.get("prompt", "")
                if not prompt_text or len(prompt_text) < 20:
                    continue

                # 提取图片URL作为预览
                image_url = img.get("url", "")
                preview_images = [image_url] if image_url else []

                # 用 reaction count 做热度
                stats = img.get("stats", {})
                reactions = (
                    stats.get("likeCount", 0) +
                    stats.get("heartCount", 0) +
                    stats.get("laughCount", 0) +
                    stats.get("cryCount", 0)
                )
                trend_score = min(100, max(10, reactions / 2))

                # 简单分类
                prompt_lower = prompt_text.lower()
                category = "其他"
                for tag, cat in [
                    ("dress", "服饰"), ("fashion", "服饰"), ("clothing", "服饰"),
                    ("makeup", "美妆"), ("skincare", "美妆"), ("cosmetic", "美妆"),
                    ("phone", "3C数码"), ("laptop", "3C数码"), ("electronic", "3C数码"),
                    ("food", "食品"), ("cake", "食品"), ("drink", "食品"),
                    ("furniture", "家居"), ("interior", "家居"), ("room", "家居"),
                    ("baby", "母婴"), ("toy", "母婴"),
                    ("sports", "运动户外"), ("running", "运动户外"), ("fitness", "运动户外"),
                    ("jewelry", "珠宝饰品"), ("necklace", "珠宝饰品"), ("ring", "珠宝饰品"),
                ]:
                    if tag in prompt_lower:
                        category = cat
                        break

                items.append({
                    "title": prompt_text[:60].replace("\n", " "),
                    "content": prompt_text,
                    "category": category,
                    "scenario": "日常种草",
                    "platform": "通用",
                    "output_type": "主图提示词",
                    "preview_images": preview_images,
                    "trend_score": trend_score,
                })

            return self.save_to_db(items)

        except Exception as e:
            print(f"[civitai] API failed: {e}")
            return 0
