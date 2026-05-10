import os
import json
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

CATEGORIES = ["服饰", "美妆", "3C数码", "食品", "家居", "母婴", "运动户外", "珠宝饰品", "其他"]
SCENARIOS = ["新品推广", "大促促销", "清仓甩卖", "日常种草", "测评推荐"]
PLATFORMS = ["淘宝", "天猫", "拼多多", "小红书", "抖音", "TikTok", "Amazon"]
OUTPUT_TYPES = ["主图提示词", "详情页文案", "标题优化", "短视频脚本", "广告投放文案"]

def classify_prompt(raw_title: str, raw_content: str) -> dict:
    if not client.api_key:
        return _fallback_classify(raw_title, raw_content)

    prompt = f"""Analyze this e-commerce AI prompt and classify it. Return ONLY a JSON object:

Title: {raw_title}
Content: {raw_content}

Return JSON with these exact keys:
- category: one of {json.dumps(CATEGORIES)}
- scenario: one of {json.dumps(SCENARIOS)}
- platform: one of {json.dumps(PLATFORMS)}
- output_type: one of {json.dumps(OUTPUT_TYPES)}
- quality_score: 1-100 (prompt structure, specificity, usability)
- enhanced_title: a clear Chinese title summarizing this prompt's use case

Return ONLY the JSON, no other text."""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return _fallback_classify(raw_title, raw_content)

def _fallback_classify(raw_title: str, raw_content: str) -> dict:
    text = (raw_title + " " + raw_content).lower()
    for cat in CATEGORIES:
        if cat.lower() in text:
            category = cat
            break
    else:
        category = "其他"

    for sc in SCENARIOS:
        if sc[:2].lower() in text:
            scenario = sc
            break
    else:
        scenario = "日常种草"

    return {
        "category": category,
        "scenario": scenario,
        "platform": "小红书",
        "output_type": "主图提示词",
        "quality_score": 50,
        "enhanced_title": raw_title[:50]
    }
