"""Main FastAPI application with enhanced error handling and middleware"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import LeadScoringException, AIServiceException, CSVProcessingException
from app.routers import offers, leads, scoring

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    yield
    logger.info("Shutting down application")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered lead scoring system combining rule-based logic with AI analysis for sales qualification",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    return response


# Exception handlers
@app.exception_handler(CSVProcessingException)
async def csv_processing_exception_handler(request: Request, exc: CSVProcessingException):
    """Handle CSV processing errors"""
    logger.error(f"CSV processing error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"error": str(exc), "type": "csv_processing_error"}
    )


@app.exception_handler(AIServiceException)
async def ai_service_exception_handler(request: Request, exc: AIServiceException):
    """Handle AI service errors"""
    logger.error(f"AI service error: {str(exc)}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "AI service temporarily unavailable. Please try again later.",
            "type": "ai_service_error",
            "provider": getattr(exc, 'provider', None)
        }
    )


@app.exception_handler(LeadScoringException)
async def lead_scoring_exception_handler(request: Request, exc: LeadScoringException):
    """Handle general lead scoring errors"""
    logger.error(f"Lead scoring error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"error": str(exc), "type": "lead_scoring_error"}
    )


# Include routers
app.include_router(offers.router, prefix="/api/v1", tags=["Offers"])
app.include_router(leads.router, prefix="/api/v1", tags=["Leads"])
app.include_router(scoring.router, prefix="/api/v1", tags=["Scoring"])


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """API information and health check"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "healthy",
        "docs_url": "/docs" if settings.debug else "Documentation available in development mode",
        "endpoints": {
            "offer": "POST /api/v1/offer",
            "upload_leads": "POST /api/v1/leads/upload",
            "score": "POST /api/v1/score",
            "results": "GET /api/v1/results",
            "export": "GET /api/v1/results/export",
            "usage_stats": "GET /api/v1/usage-stats"
        }
    }


@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )