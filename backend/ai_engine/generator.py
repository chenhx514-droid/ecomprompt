import os
import json
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

STRATEGIES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge", "prompt_strategies.json")

def generate_prompt(category: str, scenario: str, platform: str, output_type: str, description: str) -> dict:
    if not client.api_key:
        return {
            "prompt": f"[需要配置ANTHROPIC_API_KEY] Generate {output_type} for {category} {scenario} on {platform}. {description}",
            "explanation": "API key 未配置，这是占位提示词。设置环境变量 ANTHROPIC_API_KEY 后可使用完整功能。"
        }

    strategies = json.load(open(STRATEGIES_PATH, "r", encoding="utf-8"))
    skeleton = None
    for s in strategies.get("strategies", []):
        if s["category"] == category and s["scenario"] == scenario and s["output_type"] == output_type:
            skeleton = s["skeleton"]
            break

    skeleton_hint = f"\nReference structure: {skeleton}" if skeleton else ""

    prompt = f"""Generate an optimized AI prompt for e-commerce use based on these requirements:

Category: {category}
Scenario: {scenario}
Platform: {platform}
Output type: {output_type}
Additional description: {description or 'N/A'}{skeleton_hint}

Return a JSON object:
{{
  "prompt": "the complete optimized prompt text",
  "explanation": "2-3 sentence explanation of why this prompt works well for this scenario"
}}

Return ONLY the JSON, no other text."""

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)
