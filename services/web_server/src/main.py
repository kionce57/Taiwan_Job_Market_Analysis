"""FastAPI application entry point for Job Market Dashboard API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import dashboard_router

app = FastAPI(
    title="Job Market Dashboard API",
    description="Data pipeline and API for Taiwan Job Market Dashboard",
    version="0.1.0",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
