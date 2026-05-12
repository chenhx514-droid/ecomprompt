"""图片反推提示词 — 利用通义千问 Vision 分析图片并生成 AI 绘图提示词"""
import base64
import os
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from openai import OpenAI

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 4 * 1024 * 1024  # 4MB

SYSTEM_PROMPT = """You are an expert AI prompt engineer specializing in e-commerce product photography and AI image generation.

Analyze the uploaded image and return a JSON response (no markdown, raw JSON only):

{
  "prompt": "A detailed, copy-paste ready prompt in ENGLISH that describes this image. Include subject, style, lighting, composition, colors, and technical details. Make it suitable for AI image generators.",
  "prompt_cn": "中文版提示词，同样详细，适合用于Midjourney/Stable Diffusion/Flux等工具生成类似图片",
  "style": "cinematic / product photography / minimalist / illustration / 3D render / etc.",
  "composition": "describe the composition (center, rule of thirds, leading lines, etc.)",
  "lighting": "describe the lighting setup and mood",
  "colors": ["#hex1", "#hex2", "#hex3", "#hex4", "#hex5"],
  "subject": "what is the main subject of this image",
  "mood": "the overall atmosphere and feeling",
  "category": "服饰/美妆/3C数码/食品/家居/母婴/运动户外/珠宝饰品/其他",
  "negative_prompt": "things to avoid when generating similar images",
  "prompts": {
    "general": "general purpose prompt",
    "midjourney": "Midjourney style prompt with --ar and --style parameters",
    "sd": "Stable Diffusion style prompt with quality tags",
    "flux": "Flux style natural language prompt"
  }
}

Rules:
- "prompt" must be in English and very detailed (100-200 words)
- "prompt_cn" must be in Chinese and equally detailed
- "colors" must be exactly 5 hex color codes extracted from the image
- "category" must be chosen from the list based on what the product is
- Use 3-5 descriptive tags for "style"
- ALL fields are required, do not omit any"""


@router.post("/image-to-prompt")
async def image_to_prompt(
    image: UploadFile = File(...),
    model_format: str = Form("general"),
):
    # 验证文件类型
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {image.content_type}")

    # 读取并验证大小
    image_bytes = await image.read()
    if len(image_bytes) > MAX_SIZE:
        raise HTTPException(400, "Image too large (max 4MB)")

    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    print(f"[img2prompt] API key present: {bool(api_key)}, length: {len(api_key)}")

    if not api_key:
        raise HTTPException(503, "AI service not configured (missing DASHSCOPE_API_KEY)")

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # Base64 编码
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    media_type = image.content_type

    try:
        resp = client.chat.completions.create(
            model="qwen-vl-max",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{media_type};base64,{image_b64}"},
                    },
                    {
                        "type": "text",
                        "text": "Analyze this image and generate the prompt JSON. Return ONLY valid JSON, no markdown code blocks.",
                    }
                ]
            }],
            max_tokens=2000,
            temperature=0.7,
        )

        text = resp.choices[0].message.content.strip()

        # 处理 markdown code block 包装
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            if text.startswith("json"):
                text = text[4:].strip()

        result = json.loads(text)

        # 确保必填字段存在
        result.setdefault("prompts", {})
        result["prompts"].setdefault("general", result.get("prompt", ""))
        result["prompts"].setdefault("midjourney", result.get("prompt", ""))
        result["prompts"].setdefault("sd", result.get("prompt", ""))
        result["prompts"].setdefault("flux", result.get("prompt", ""))

        return result

    except json.JSONDecodeError:
        return {
            "prompt": text[:500] if 'text' in dir() else "",
            "prompt_cn": "",
            "style": "unknown",
            "composition": "",
            "lighting": "",
            "colors": [],
            "subject": "",
            "mood": "",
            "category": "其他",
            "negative_prompt": "",
            "prompts": {
                "general": text[:500] if 'text' in dir() else "",
                "midjourney": text[:500] if 'text' in dir() else "",
                "sd": text[:500] if 'text' in dir() else "",
                "flux": text[:500] if 'text' in dir() else "",
            }
        }
    except Exception as e:
        raise HTTPException(500, f"AI analysis failed: {str(e)}")
