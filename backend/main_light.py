"""轻量启动 — 加载所有爬虫数据 + API 服务"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import init_db
import threading
import os

app = FastAPI(title="EcomPrompt API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_seed():
    print("[startup] Loading seed data...")
    from crawler.promptbase import PromptBaseCrawler
    count = PromptBaseCrawler().run()
    print(f"[startup] Seed: {count} prompts")

def run_crawlers():
    """在后台依次运行所有爬虫"""
    from crawler import CRAWLERS
    for name, crawler in CRAWLERS.items():
        if name == "promptbase":
            continue  # seed 已经加载过了
        print(f"[startup] Crawling {name}...")
        try:
            count = crawler.run()
            print(f"[startup] {name}: {count} new prompts")
        except Exception as e:
            print(f"[startup] {name} failed: {e}")

@app.on_event("startup")
async def startup():
    init_db()
    load_seed()
    # 后台跑其他爬虫，不阻塞启动
    t = threading.Thread(target=run_crawlers)
    t.start()

# 注册路由
from api.prompts import router as prompts_router
from api.trends import router as trends_router
from api.import_data import router as import_router
from api.collect import router as collect_router
from api.auth import router as auth_router

app.include_router(prompts_router, prefix="/api", tags=["prompts"])
app.include_router(trends_router, prefix="/api", tags=["trends"])
app.include_router(import_router, prefix="/api", tags=["import"])
app.include_router(collect_router, prefix="/api", tags=["collect"])
app.include_router(auth_router, prefix="/api", tags=["auth"])

# 静态文件服务 — 上传的图片
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "images"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/api/images", StaticFiles(directory=UPLOAD_DIR), name="images")

@app.get("/api/health")
def health():
    return {"status": "ok"}

# AI generate 需要 API key
try:
    from api.generate import router as generate_router
    app.include_router(generate_router, prefix="/api", tags=["generate"])
    print("[startup] AI generate API loaded")
except Exception as e:
    print(f"[startup] AI generate API skipped: {e}")

# 手动触发爬虫
@app.post("/api/crawl")
def trigger_crawl():
    t = threading.Thread(target=run_crawlers)
    t.start()
    return {"ok": True, "message": "Crawlers started in background"}

# 生产环境：serve 前端静态文件（必须在所有 /api 路由注册之后）
FRONTEND_DIR = os.environ.get("FRONTEND_DIR", os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    print(f"[startup] Serving frontend from {FRONTEND_DIR}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
