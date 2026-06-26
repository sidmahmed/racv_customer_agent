from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import chat

app = FastAPI(title="Agentic Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Registered twice: bare (matches what arrives once Vercel's "Services" router
# strips the `/api` routePrefix before invoking this app) and again under
# `/api` (matches plain `uv run uvicorn` local dev, where there's no
# stripping layer and the frontend's hardcoded `/api/...` fetch calls hit
# this app directly).
app.include_router(chat.router)
app.include_router(chat.router, prefix="/api")
app.add_api_route("/api/health", health, methods=["GET"])
