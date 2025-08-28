"""
SupplyChainRescue AI - FastAPI Backend
Main application entry point for the disaster relief optimization system.
"""
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

# Import local modules
from backend.config import settings
from backend.models.schemas import APIResponse

# Import route modules
from backend.routes.roads import router as roads_router
from backend.routes.weather import router as weather_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting SupplyChainRescue AI backend...")
    # TODO: Initialize database connections, ML models, etc.
    yield
    logger.info("Shutting down SupplyChainRescue AI backend...")
    # TODO: Cleanup resources


# Create FastAPI app instance
app = FastAPI(
    title="SupplyChainRescue AI",
    description="AI-powered disaster relief supply chain optimization",
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs",  # Swagger documentation
    redoc_url="/redoc"  # ReDoc documentation
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled errors"""
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=APIResponse(
            success=False,
            message="An unexpected error occurred",
            data={"error": str(
                exc) if settings.debug else "Internal server error"}
        ).dict()
    )

# API v1 routes
app.include_router(
    roads_router,
    prefix=settings.api_v1_prefix + "/roads",
    tags=["roads"]
)

app.include_router(
    weather_router,
    prefix=settings.api_v1_prefix + "/weather",
    tags=["weather"]
)

# Health check endpoints


@app.get("/health")
async def health_check():
    """Main health check endpoint"""
    return APIResponse(
        success=True,
        message="SupplyChainRescue AI backend is healthy",
        data={
            "version": settings.version,
            "services": {
                "roads": "operational",
                "weather": "operational" if settings.openweather_api_key else "needs_api_key",
                "database": "operational",  # TODO: Check actual DB connection
            }
        }
    ).dict()


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system information"""
    import platform

    # Mock system info for now - will integrate psutil in Day 2
    health_info = {
        "version": settings.version,
        "timestamp": "2024-01-15T10:30:00Z",  # TODO: Use actual timestamp
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": 4,  # Mock value
            "memory": {
                "total_mb": 8192,  # Mock value
                "available_mb": 4096,  # Mock value
                "percent_used": 50.0  # Mock value
            }
        },
        "services": {
            "roads_api": "operational",
            "weather_api": "operational" if settings.openweather_api_key else "api_key_required",
            "database": "operational"  # TODO: Check actual DB status
        },
        "features": {
            "weather_forecast": bool(settings.openweather_api_key),
            "route_optimization": False,  # TODO: Add OR-Tools integration
            "ml_forecasting": False,  # TODO: Add ML model loading status
            "osm_integration": False,  # TODO: Add OpenStreetMap integration
        }
    }

    return APIResponse(
        success=True,
        message="Detailed health information",
        data=health_info
    ).dict()


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return APIResponse(
        success=True,
        message=f"Welcome to SupplyChainRescue AI v{settings.version}",
        data={
            "description": "AI-powered disaster relief supply chain optimization",
            "version": settings.version,
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc"
            },
            "endpoints": {
                "roads": settings.api_v1_prefix + "/roads",
                "weather": settings.api_v1_prefix + "/weather"
            }
        }
    ).dict()

# TODO: Add more routers as per roadmap:
# - /api/v1/forecast - Forecasting models
# - /api/v1/reports - Situation reports
# - /api/v1/optimize - Route optimization

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
