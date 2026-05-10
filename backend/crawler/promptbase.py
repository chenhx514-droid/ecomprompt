from .base import BaseCrawler

class PromptBaseCrawler(BaseCrawler):
    name = "promptbase"

    def run(self) -> int:
        seed_prompts = [
            {
                "title": "夏季新款连衣裙电商主图",
                "content": "E-commerce product photography of a flowy summer maxi dress, soft pastel floral print, model standing in sunlit garden at golden hour, fabric details visible, professional fashion photography, 8K resolution, clean composition, natural lighting, full body shot and detail close-up, white wooden background, minimalist aesthetic",
                "category": "服饰", "scenario": "新品推广", "platform": "淘宝",
                "output_type": "主图提示词", "trend_score": 92
            },
            {
                "title": "618大促美妆礼盒展示",
                "content": "Luxury skincare gift box flat lay photography, rose gold packaging, surrounded by fresh rose petals, marble background, soft natural light from window, high-end cosmetic branding style, 5 products arranged in elegant composition, macro details of texture, premium gift packaging visible, Mother's Day gift theme",
                "category": "美妆", "scenario": "大促促销", "platform": "天猫",
                "output_type": "主图提示词", "trend_score": 88
            },
            {
                "title": "无线蓝牙耳机种草文案",
                "content": "Write 5 Instagram-style product captions for wireless earbuds targeting young professionals (25-35). Each caption should include: 1) pain point (tangled wires, bad call quality) 2) solution hook 3) key feature (battery life, noise cancelling, design) 4) social proof (ratings/reviews angle) 5) CTA with emoji. Tone: casual and relatable. Max 150 chars each. Include relevant hashtags.",
                "category": "3C数码", "scenario": "日常种草", "platform": "小红书",
                "output_type": "文案提示词", "trend_score": 85
            },
            {
                "title": "国风零食短视频脚本",
                "content": "Create a 30-second Douyin/TikTok video script for traditional Chinese snacks (lotus seed cake, osmanthus cake). Opening hook: unexpected texture reveal (0-3s). Middle: close-up shots of packaging opening, steaming hot snack, bite shot with audio of crunch (3-25s). End: limited-time discount overlay + 'link in bio' CTA (25-30s). Voiceover: nostalgic storytelling tone, mention 'taste of childhood'. Lighting: warm, cozy kitchen vibe.",
                "category": "食品", "scenario": "新品推广", "platform": "抖音",
                "output_type": "短视频脚本", "trend_score": 79
            },
            {
                "title": "智能家居产品详情页文案",
                "content": "Write a complete product detail page copy for a smart robot vacuum cleaner. Sections needed: 1) Hero headline (8-12 words, emotional + functional) 2) Product highlights (5 bullet points, each with feature + benefit + tech spec) 3) Usage scenario description (200 words, paint picture of clean home without effort) 4) Comparison table (vs traditional vacuum, vs previous gen) 5) Technical specs (organized by category: cleaning, navigation, smart features) 6) FAQ section 7) Final CTA with limited-time offer. Tone: trustworthy expert with warmth. Keywords for SEO: smart home, robot vacuum, automatic cleaning, LDS navigation.",
                "category": "家居", "scenario": "日常种草", "platform": "Amazon",
                "output_type": "详情页文案", "trend_score": 76
            },
            {
                "title": "母婴纸尿裤大促标题优化",
                "content": "Generate 10 SEO-optimized product titles for premium baby diapers on Tmall during 618 sale. Include: brand placeholder + key specs (ultra-thin, breathable, 12h absorption) + age range (0-12 months) + quantity in pack + 618 deal angle + emoji. Max 40 chars per title. Titles should balance search keywords with emotional parent appeal.",
                "category": "母婴", "scenario": "大促促销", "platform": "天猫",
                "output_type": "标题优化", "trend_score": 82
            },
            {
                "title": "运动跑鞋户外场景拍摄",
                "content": "Action sports photography of running shoes, male runner mid-stride on mountain trail at sunrise, dynamic motion capture, sweat details, shoe sole grip visible on rocky terrain, breathable mesh upper close-up, athletic lifestyle aesthetic, golden morning light through trees, professional sports advertising style, shallow depth of field on shoes, energy and performance mood",
                "category": "运动户外", "scenario": "新品推广", "platform": "拼多多",
                "output_type": "主图提示词", "trend_score": 74
            },
            {
                "title": "轻奢首饰品牌小红书笔记",
                "content": "Write a Xiaohongshu (RED) post for a minimalist 18K gold necklace. Structure: 1) Attention-grabbing headline with symbol [] 2) Personal story hook (received as gift / treating myself) 3) 3-4 detail photos description (layering, close-up of clasp, matching outfits) 4) Why this piece is worth it (material, design, versatility) 5) Price transparency + where to buy 6) 5-8 relevant tags. Include emoji throughout. Tone: genuine sharing between girlfriends, not hard sell. End with question to drive comments.",
                "category": "珠宝饰品", "scenario": "日常种草", "platform": "小红书",
                "output_type": "文案提示词", "trend_score": 71
            },
        ]
        return self.save_to_db(seed_prompts)
