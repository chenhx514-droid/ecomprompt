import os
import json
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

STRATEGIES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge", "prompt_strategies.json")

def load_strategies():
    with open(STRATEGIES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("strategies", [])

def find_strategy(category: str, scenario: str, output_type: str):
    strategies = load_strategies()
    for s in strategies:
        if s["category"] == category and s["scenario"] == scenario and s["output_type"] == output_type:
            return s["skeleton"]
    return None

def enhance_prompt(raw_content: str, category: str, scenario: str, platform: str, output_type: str) -> str:
    skeleton = find_strategy(category, scenario, output_type)
    if not client.api_key:
        return raw_content

    skeleton_hint = f"\nReference skeleton: {skeleton}" if skeleton else ""

    prompt = f"""Optimize this e-commerce AI prompt for better results. Make it more specific, structured, and effective.

Original prompt: {raw_content}
Category: {category}
Scenario: {scenario}
Platform: {platform}
Output type: {output_type}{skeleton_hint}

Return ONLY the enhanced prompt text. No explanation."""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text.strip()
    except Exception:
        return raw_content
