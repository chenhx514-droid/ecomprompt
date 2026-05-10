from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import prompts, generate, trends, import_data
from database import init_db
from scheduler import start_scheduler

app = FastAPI(title="EcomPrompt API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompts.router, prefix="/api", tags=["prompts"])
app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(trends.router, prefix="/api", tags=["trends"])
app.include_router(import_data.router, prefix="/api", tags=["import"])

@app.on_event("startup")
async def startup():
    init_db()
    start_scheduler()

@app.get("/api/health")
def health():
    return {"status": "ok"}
