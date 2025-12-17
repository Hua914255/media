from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import story, metrics, ws

app = FastAPI(title="Story Lab API", version="1.0.0")

# 开发阶段直接放开，线上再收紧
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(story.router, prefix="/api/story", tags=["story"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(ws.router, tags=["ws"])
