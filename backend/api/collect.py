"""个人收录：上传图片 + 提示词（需登录）"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from database import get_connection
from api.auth import get_current_user
import json
import os
import uuid
import shutil

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

@router.post("/collect")
async def collect_prompt(
    title: str = Form(...),
    category: str = Form("其他"),
    scenario: str = Form("日常种草"),
    platform: str = Form("通用"),
    output_type: str = Form("主图提示词"),
    content: str = Form(...),
    folder: str = Form("默认"),
    images: list[UploadFile] = File(default=[]),
    current_user: dict = Depends(get_current_user),
):
    preview_images = []

    for img in images:
        if not img.filename:
            continue
        ext = os.path.splitext(img.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue

        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, unique_name)

        with open(filepath, "wb") as f:
            shutil.copyfileobj(img.file, f)

        preview_images.append(f"/api/images/{unique_name}")

    conn = get_connection()
    conn.execute(
        """INSERT INTO prompts
           (title, category, scenario, platform, content, output_type,
            preview_images, trend_score, source, collection_folder, user_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'user_collect', ?, ?)""",
        (
            title, category, scenario, platform, content, output_type,
            json.dumps(preview_images), 60.0, folder, current_user["user_id"],
        )
    )
    conn.commit()
    conn.close()

    return {
        "ok": True,
        "message": "收录成功",
        "images_saved": len(preview_images),
    }

@router.get("/folders")
def list_folders(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT collection_folder FROM prompts WHERE source = 'user_collect' AND user_id = ? ORDER BY collection_folder",
        (current_user["user_id"],)
    ).fetchall()
    conn.close()
    folders = [row[0] for row in rows]
    if "默认" not in folders:
        folders.insert(0, "默认")
    return {"folders": folders}
