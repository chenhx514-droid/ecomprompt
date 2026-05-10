from fastapi import APIRouter, UploadFile, File, HTTPException
from database import get_connection
import csv
import io
import json

router = APIRouter()

@router.post("/import")
async def import_file(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename or "unknown"
    rows = []
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "csv":
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        rows = [row for row in reader]
    elif ext == "json":
        rows = json.loads(content)
        if isinstance(rows, dict):
            rows = [rows]
    else:
        raise HTTPException(status_code=400, detail="仅支持 CSV 和 JSON 格式")

    conn = get_connection()
    imported = 0
    trends_map = {}

    for row in rows:
        category = row.get("category", row.get("品类", "其他"))
        keyword = row.get("keyword", row.get("关键词", row.get("title", "")))
        heat = float(row.get("heat", row.get("热度", 50)))

        conn.execute(
            "INSERT INTO trends (category, keyword, heat, source) VALUES (?, ?, ?, 'user_import')",
            (category, str(keyword), heat)
        )
        imported += 1

        if category not in trends_map:
            trends_map[category] = 0
        trends_map[category] += 1

    conn.execute(
        "INSERT INTO import_logs (filename, row_count, trends_extracted) VALUES (?, ?, ?)",
        (filename, imported, len(trends_map))
    )
    conn.commit()
    conn.close()

    return {
        "ok": True,
        "imported": imported,
        "categories_found": list(trends_map.keys()),
        "trends_extracted": len(trends_map)
    }
