from fastapi import APIRouter, HTTPException
from models import GenerateRequest, GenerateResponse
from ai_engine.generator import generate_prompt

router = APIRouter()

@router.post("/generate")
def generate(req: GenerateRequest):
    result = generate_prompt(
        category=req.category,
        scenario=req.scenario,
        platform=req.platform,
        output_type=req.output_type,
        description=req.description
    )
    return GenerateResponse(**result)

@router.post("/enhance/{prompt_id}")
def enhance_prompt(prompt_id: int):
    from database import get_connection
    from ai_engine.enhancer import enhance_prompt
    conn = get_connection()
    row = conn.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404)
    d = dict(row)
    enhanced = enhance_prompt(
        raw_content=d["content"],
        category=d["category"],
        scenario=d["scenario"],
        platform=d["platform"],
        output_type=d["output_type"]
    )
    conn.execute(
        "UPDATE prompts SET content = ?, updated_at = datetime('now') WHERE id = ?",
        (enhanced, prompt_id)
    )
    conn.commit()
    conn.close()
    return {"enhanced": enhanced}
