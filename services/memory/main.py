import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as memory_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIMemoryLayer - Core Memory Service",
    description="Enterprise middleware for AI agent persistent context and semantic memory.",
    version="0.1.0",
)

# Enterprise CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # In production, restrict this to the API Gateway/Frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Support both versioned and unversioned routes for better DX
app.include_router(memory_router, prefix="/v1")
app.include_router(memory_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "memory-service"}
