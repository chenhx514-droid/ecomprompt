"""LiblibAI 爬虫 — 抓取国内AI绘画平台的提示词和图片

LiblibAI (liblib.art) 是国内最大的AI绘画模型/图片分享社区。
页面结构会变化，需要定期更新CSS选择器。
"""

from .base import BaseCrawler
import re

class LiblibCrawler(BaseCrawler):
    name = "liblib"

    # LiblibAI 的公开API入口（无需登录）
    API_BASE = "https://www.liblib.art/api"

    def run(self) -> int:
        total = 0
        # 尝试多个API端点
        for endpoint in self._get_endpoints():
            try:
                count = self._fetch_page(endpoint)
                total += count
                if total >= 20:
                    break
            except Exception as e:
                print(f"[liblib] {endpoint}: {e}")
                continue

        # 如果API全部失败，用种子数据兜底
        if total == 0:
            print("[liblib] API failed, using fallback data")
            total = self._fallback()
        return total

    def _get_endpoints(self):
        """LiblibAI 可能的公开端点"""
        return [
            "/sqad/community/image/v2/list?type=hot&pageSize=20&pageNum=1",
            "/sqad/community/image/v2/list?type=new&pageSize=20&pageNum=1",
            "/community/image/list?sort=hot&pageSize=20&pageNum=1",
        ]

    def _fetch_page(self, endpoint: str) -> int:
        url = f"{self.API_BASE}{endpoint}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.liblib.art/",
            "Accept": "application/json",
        }
        # 直接用 httpx client 请求
        import httpx
        with httpx.Client(timeout=15) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        items = []
        image_list = []
        if isinstance(data, dict):
            image_list = (
                data.get("data", {}).get("list", []) or
                data.get("data", {}).get("data", []) or
                data.get("data", []) or
                []
            )

        for img in image_list:
            prompt = img.get("prompt") or img.get("meta", {}).get("prompt", "")
            if not prompt or len(prompt) < 15:
                continue

            img_url = img.get("imageUrl") or img.get("url") or img.get("thumbUrl", "")
            preview = [img_url] if img_url else []

            title = (img.get("title") or prompt)[:60].replace("\n", " ")
            like_count = img.get("likeCount") or img.get("likeNum") or 0
            trend = min(100, max(10, int(like_count) / 5))

            items.append({
                "title": title,
                "content": prompt,
                "category": self._guess_cat(prompt),
                "scenario": "日常种草",
                "platform": "通用",
                "output_type": "主图提示词",
                "preview_images": preview,
                "trend_score": trend,
            })

        return self.save_to_db(items)

    def _guess_cat(self, text: str) -> str:
        text = text.lower()
        for kw, cat in [
            ("dress", "服饰"), ("fashion", "服饰"), ("clothing", "服饰"), ("旗袍", "服饰"), ("汉服", "服饰"),
            ("makeup", "美妆"), ("skincare", "美妆"), ("口红", "美妆"), ("护肤", "美妆"),
            ("phone", "3C数码"), ("earphone", "3C数码"), ("手机", "3C数码"),
            ("food", "食品"), ("cake", "食品"), ("美食", "食品"), ("甜点", "食品"),
            ("furniture", "家居"), ("interior", "家居"), ("room", "家居"), ("家具", "家居"),
            ("baby", "母婴"), ("toy", "母婴"), ("儿童", "母婴"),
            ("sports", "运动户外"), ("outdoor", "运动户外"), ("运动", "运动户外"),
            ("jewelry", "珠宝饰品"), ("necklace", "珠宝饰品"), ("项链", "珠宝饰品"),
        ]:
            if kw in text:
                return cat
        return "其他"

    def _fallback(self) -> int:
        """国内常用提示词种子"""
        seeds = [
            {
                "title": "新中式女装电商主图", "category": "服饰", "scenario": "新品推广", "platform": "淘宝",
                "output_type": "主图提示词", "trend_score": 93,
                "preview_images": ["https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&h=400&fit=crop"],
                "content": "新中式风格女装拍摄，改良旗袍连衣裙，真丝面料质感，中国风庭院背景，竹林光影，模特侧身站姿，柔光滤镜，高级感，淘宝主图风格，8K超清，细节特写，盘扣和刺绣细节清晰可见"
            },
            {
                "title": "国潮美妆礼盒短视频", "category": "美妆", "scenario": "大促促销", "platform": "抖音",
                "output_type": "短视频脚本", "trend_score": 90,
                "preview_images": ["https://images.unsplash.com/photo-1596704017254-9b121068fb31?w=600&h=400&fit=crop"],
                "content": "国潮风美妆礼盒开箱视频脚本。0-3s：礼盒特写，丝带缓缓拉开。3-10s：逐个展示产品（口红、眼影、散粉），每件产品搭配对应使用效果画面切换。10-20s：完整妆容变身，素颜到全妆的快速过渡。20-30s：礼盒全景展示+价格+购买链接。BGM：轻快中国风电子乐。"
            },
            {
                "title": "露营装备详情页设计", "category": "运动户外", "scenario": "新品推广", "platform": "拼多多",
                "output_type": "详情页文案", "trend_score": 81,
                "preview_images": ["https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=600&h=400&fit=crop"],
                "content": "户外露营帐篷产品详情页文案。板块：1)主标题：一帐之间，把家搬进山野。2)卖点（防暴雨+速开+透气防蚊+轻量化2.1kg）。3)场景描述：周末逃离城市，带着这款帐篷去拥抱星空。4)参数对比表。5)好评精选。目标人群：25-35岁城市白领露营新手。"
            },
            {
                "title": "零食大礼包直播话术", "category": "食品", "scenario": "清仓甩卖", "platform": "抖音",
                "output_type": "文案提示词", "trend_score": 77,
                "preview_images": ["https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=600&h=400&fit=crop"],
                "content": "直播间零食大礼包促销话术：'家人们看过来！今天这款零食大礼包，原价99，今天直播间专属价只要39.9！里面有牛肉干、坚果、薯片整整15包！看一下这个牛肉干，拉丝的！再看这个坚果，颗颗饱满！买到就是赚到，库存只有200单，手慢无！' 需要制造紧迫感，语速快速，重复强调价格优势。"
            },
        ]
        return self.save_to_db(seeds)
