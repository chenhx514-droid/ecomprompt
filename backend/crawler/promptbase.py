from .base import BaseCrawler

class PromptBaseCrawler(BaseCrawler):
    name = "promptbase"

    def run(self) -> int:
        seeds = [
            {
                "title": "夏季连衣裙电商主图",
                "category": "服饰", "scenario": "新品推广", "platform": "淘宝",
                "output_type": "主图提示词", "trend_score": 95,
                "preview_images": [
                    "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&h=400&fit=crop",
                    "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&h=400&fit=crop"
                ],
                "content": "E-commerce product photography of a flowy summer maxi dress, soft pastel floral print, model standing in sunlit garden at golden hour, fabric details visible, professional fashion photography, 8K resolution, clean composition, natural lighting, full body shot and detail close-up, white wooden background, minimalist aesthetic"
            },
            {
                "title": "618大促美妆礼盒展示",
                "category": "美妆", "scenario": "大促促销", "platform": "天猫",
                "output_type": "主图提示词", "trend_score": 91,
                "preview_images": [
                    "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&h=400&fit=crop",
                    "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&h=400&fit=crop"
                ],
                "content": "Luxury skincare gift box flat lay photography, rose gold packaging, surrounded by fresh rose petals, marble background, soft natural light from window, high-end cosmetic branding style, 5 products arranged in elegant composition, macro details of texture, premium gift packaging visible"
            },
            {
                "title": "蓝牙耳机小红书种草文案",
                "category": "3C数码", "scenario": "日常种草", "platform": "小红书",
                "output_type": "文案提示词", "trend_score": 88,
                "preview_images": [
                    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop"
                ],
                "content": "Write 5 Instagram-style product captions for wireless earbuds targeting young professionals (25-35). Each caption: 1) pain point (tangled wires, bad call quality) 2) solution hook 3) key feature (battery life, noise cancelling, design) 4) social proof (ratings/reviews angle) 5) CTA with emoji. Max 150 chars each. Include relevant hashtags."
            },
            {
                "title": "国风糕点抖音短视频脚本",
                "category": "食品", "scenario": "新品推广", "platform": "抖音",
                "output_type": "短视频脚本", "trend_score": 84,
                "preview_images": [
                    "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600&h=400&fit=crop",
                    "https://images.unsplash.com/photo-1495147466023-ac5c588e2e94?w=600&h=400&fit=crop"
                ],
                "content": "Create a 30-second Douyin video script for traditional Chinese pastries. Opening hook: steaming hot pastry broken in half, filling oozing out (0-3s). Middle: close-up shots of handmade process, golden bake color, bite shot with crunch audio (3-25s). End: limited-time discount overlay + 'link in bio' CTA (25-30s). Voiceover: nostalgic storytelling about taste of childhood. Warm kitchen lighting."
            },
            {
                "title": "扫地机器人详情页文案",
                "category": "家居", "scenario": "日常种草", "platform": "Amazon",
                "output_type": "详情页文案", "trend_score": 82,
                "preview_images": [
                    "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600&h=400&fit=crop"
                ],
                "content": "Write a complete product detail page copy for a smart robot vacuum cleaner. Sections: 1) Hero headline (emotional + functional, 8-12 words) 2) Product highlights (5 bullet points, feature + benefit + tech spec) 3) Usage scenario description (200 words, paint a picture of clean home without effort) 4) Comparison table (vs traditional vacuum, vs previous gen) 5) Technical specs 6) FAQ section 7) Final CTA with limited-time offer. Tone: trustworthy expert with warmth."
            },
            {
                "title": "母婴纸尿裤大促标题优化",
                "category": "母婴", "scenario": "大促促销", "platform": "天猫",
                "output_type": "标题优化", "trend_score": 86,
                "preview_images": [
                    "https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=600&h=400&fit=crop"
                ],
                "content": "Generate 10 SEO-optimized product titles for premium baby diapers on Tmall during 618 sale. Include: brand placeholder + key specs (ultra-thin, breathable, 12h absorption) + age range (0-12 months) + quantity in pack + 618 deal angle + emoji. Max 40 chars per title. Balance search keywords with emotional parent appeal."
            },
            {
                "title": "运动跑鞋户外场景拍摄",
                "category": "运动户外", "scenario": "新品推广", "platform": "拼多多",
                "output_type": "主图提示词", "trend_score": 78,
                "preview_images": [
                    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&h=400&fit=crop",
                    "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600&h=400&fit=crop"
                ],
                "content": "Action sports photography of running shoes, male runner mid-stride on mountain trail at sunrise, dynamic motion capture, sweat details, shoe sole grip visible on rocky terrain, breathable mesh upper close-up, athletic lifestyle aesthetic, golden morning light through trees, professional sports advertising style, shallow depth of field on shoes"
            },
            {
                "title": "轻奢项链小红书种草笔记",
                "category": "珠宝饰品", "scenario": "日常种草", "platform": "小红书",
                "output_type": "文案提示词", "trend_score": 76,
                "preview_images": [
                    "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&h=400&fit=crop",
                    "https://images.unsplash.com/photo-1599643478518-a530eab15eaa?w=600&h=400&fit=crop"
                ],
                "content": "Write a Xiaohongshu (RED) post for a minimalist 18K gold necklace. Structure: 1) Attention-grabbing headline [] 2) Personal story hook (treating myself) 3) 3-4 detail photos description (layering, close-up of clasp, matching outfits) 4) Why this piece is worth it (material, design, versatility) 5) Price transparency + where to buy 6) 5-8 relevant tags. Genuine sharing between girlfriends, not hard sell. End with question to drive comments."
            },
            {
                "title": "防晒霜夏季大促主图",
                "category": "美妆", "scenario": "大促促销", "platform": "天猫",
                "output_type": "主图提示词", "trend_score": 89,
                "preview_images": [
                    "https://images.unsplash.com/photo-1570194065650-d99fb4ee8e39?w=600&h=400&fit=crop"
                ],
                "content": "Professional beauty product photography, sunscreen bottle on white marble surface, surrounded by tropical leaves and a slice of coconut, bright summer sunlight streaming in, water droplets on the bottle, refreshing summer vibe, high-end cosmetic advertising style, clean minimalist composition, 8K resolution"
            },
            {
                "title": "手机壳拼多多爆款文案",
                "category": "3C数码", "scenario": "清仓甩卖", "platform": "拼多多",
                "output_type": "文案提示词", "trend_score": 73,
                "preview_images": [
                    "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=600&h=400&fit=crop"
                ],
                "content": "Write 10 Pinduoduo-style product descriptions for trendy phone cases. Each: attention-grabbing emoji + urgent scarcity language + key feature (shockproof, slim, cute design) + price comparison (was X, now Y) + social proof (X sold today). Max 80 chars each. Tone: energetic, FOMO-driven, friendly."
            },
            {
                "title": "居家香薰蜡烛场景图拍摄",
                "category": "家居", "scenario": "日常种草", "platform": "小红书",
                "output_type": "主图提示词", "trend_score": 75,
                "preview_images": [
                    "https://images.unsplash.com/photo-1602874801006-14f8b55ed2ce?w=600&h=400&fit=crop"
                ],
                "content": "Cozy home ambiance photography, scented soy candle burning on wooden coffee table, soft knitted blanket draped nearby, steaming cup of tea, open book, warm fairy lights in background, rainy window, hygge lifestyle aesthetic, shallow depth of field, warm golden tones, 8K"
            },
            {
                "title": "宠物用品亚马逊Listing优化",
                "category": "母婴", "scenario": "日常种草", "platform": "Amazon",
                "output_type": "详情页文案", "trend_score": 70,
                "preview_images": [
                    "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=400&fit=crop"
                ],
                "content": "Write Amazon A+ content for premium dog bed. Include: brand story, 5 image-text modules (orthopedic foam, washable cover, non-slip bottom, size guide, color options), comparison chart vs competitors, customer review highlights, and SEO backend keywords. Target: dog owners who treat pets as family. Tone: caring expert."
            },
        ]
        return self.save_to_db(seeds)
