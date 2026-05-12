"""个人仓库 API — 查看、删除、移动收藏的提示词"""
from fastapi import APIRouter, Depends, HTTPException
from database import get_connection
from api.auth import get_current_user

router = APIRouter()


@router.get("/library/stats")
def library_stats(current_user: dict = Depends(get_current_user)):
    """返回当前用户的收藏统计"""
    conn = get_connection()
    user_id = current_user["user_id"]

    total = conn.execute(
        "SELECT COUNT(*) FROM prompts WHERE source = 'user_collect' AND user_id = ?",
        (user_id,)
    ).fetchone()[0]

    by_category = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM prompts WHERE source = 'user_collect' AND user_id = ? GROUP BY category ORDER BY cnt DESC",
        (user_id,)
    ).fetchall()

    by_folder = conn.execute(
        "SELECT collection_folder, COUNT(*) as cnt FROM prompts WHERE source = 'user_collect' AND user_id = ? GROUP BY collection_folder ORDER BY cnt DESC",
        (user_id,)
    ).fetchall()

    folders = [row[0] for row in by_folder]

    conn.close()
    return {
        "total": total,
        "categories": [{"name": r[0], "count": r[1]} for r in by_category],
        "folders": folders,
    }


@router.delete("/library/{prompt_id}")
def delete_prompt(prompt_id: int, current_user: dict = Depends(get_current_user)):
    """删除收藏的提示词（仅限自己的）"""
    conn = get_connection()
    user_id = current_user["user_id"]

    row = conn.execute(
        "SELECT id, user_id, preview_images FROM prompts WHERE id = ?",
        (prompt_id,)
    ).fetchone()

    if not row:
        conn.close()
        raise HTTPException(404, "提示词不存在")
    if row[1] != user_id:
        conn.close()
        raise HTTPException(403, "无权删除他人的内容")

    # 清理关联的图片文件
    import json, os
    try:
        images = json.loads(row[2] or "[]")
        for img_url in images:
            filename = img_url.rsplit("/", 1)[-1] if "/" in img_url else ""
            if filename:
                img_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "images", filename
                )
                if os.path.isfile(img_path):
                    os.remove(img_path)
    except Exception:
        pass

    conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    conn.commit()
    conn.close()
    return {"ok": True, "message": "已删除"}


@router.put("/library/{prompt_id}/folder")
def move_folder(
    prompt_id: int,
    folder: str,
    current_user: dict = Depends(get_current_user)
):
    """移动提示词到另一个文件夹"""
    conn = get_connection()
    user_id = current_user["user_id"]

    row = conn.execute(
        "SELECT id, user_id FROM prompts WHERE id = ?",
        (prompt_id,)
    ).fetchone()

    if not row:
        conn.close()
        raise HTTPException(404, "提示词不存在")
    if row[1] != user_id:
        conn.close()
        raise HTTPException(403, "无权修改他人的内容")

    conn.execute(
        "UPDATE prompts SET collection_folder = ? WHERE id = ?",
        (folder, prompt_id)
    )
    conn.commit()
    conn.close()
    return {"ok": True, "message": f"已移至 {folder}"}
