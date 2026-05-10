from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from database import get_connection
from models import Prompt, PromptListResponse
from api.auth import get_optional_user
import json

router = APIRouter()

@router.get("/prompts")
def list_prompts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str = Query(""),
    scenario: str = Query(""),
    platform: str = Query(""),
    output_type: str = Query(""),
    sort: str = Query("trend_score"),
    search: str = Query(""),
    source: str = Query(""),
    folder: str = Query(""),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    conn = get_connection()
    conditions = []
    params = []

    if category:
        conditions.append("category = ?")
        params.append(category)
    if scenario:
        conditions.append("scenario = ?")
        params.append(scenario)
    if platform:
        conditions.append("platform = ?")
        params.append(platform)
    if output_type:
        conditions.append("output_type = ?")
        params.append(output_type)
    if source:
        if source == "user_collect":
            if current_user is None:
                conn.close()
                return PromptListResponse(items=[], total=0, page=page, page_size=page_size)
            conditions.append("user_id = ?")
            params.append(current_user["user_id"])
        conditions.append("source = ?")
        params.append(source)
    if folder:
        conditions.append("collection_folder = ?")
        params.append(folder)
    if search:
        conditions.append("(title LIKE ? OR content LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    valid_sorts = {"trend_score", "usage_count", "updated_at"}
    order_by = sort if sort in valid_sorts else "trend_score"

    total = conn.execute(f"SELECT COUNT(*) FROM prompts {where}", params).fetchone()[0]
    offset = (page - 1) * page_size
    sql = f"SELECT * FROM prompts {where} ORDER BY {order_by} DESC LIMIT ? OFFSET ?"
    rows = conn.execute(sql, params + [page_size, offset]).fetchall()

    items = []
    for row in rows:
        d = dict(row)
        items.append(Prompt(**d))

    conn.close()
    return PromptListResponse(items=items, total=total, page=page, page_size=page_size)

@router.get("/prompts/{prompt_id}")
def get_prompt(prompt_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Prompt not found")
    d = dict(row)
    return Prompt(**d)

@router.post("/prompts/{prompt_id}/use")
def increment_usage(prompt_id: int):
    conn = get_connection()
    conn.execute("UPDATE prompts SET usage_count = usage_count + 1 WHERE id = ?", (prompt_id,))
    conn.commit()
    conn.close()
    return {"ok": True}
