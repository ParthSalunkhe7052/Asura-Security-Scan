from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.database import init_db, SessionLocal
from app.api import projects, scans, metrics, reports, comparison, notifications
from app.utils.dependency_checker import DependencyChecker
from app.models.models import Config
import time
import json
import os
import logging

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger("asura")

ENV = os.getenv("ENV", "dev").lower()

app = FastAPI(
    title="ASURA SecureLab API",
    description="Security scanner and code quality analysis API",
    version="0.3.0"
)

# Request size limit middleware (10MB)
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request body size to prevent memory exhaustion"""
    content_length = request.headers.get("content-length")
    if content_length:
        content_length = int(content_length)
        if content_length > MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": f"Request too large. Maximum size: {MAX_REQUEST_SIZE / 1024 / 1024}MB"
                }
            )
    
    response = await call_next(request)
    return response

class RateLimiter:
    def __init__(self, requests_per_window: int, window_seconds: int, burst: int = None):
        self.rpw = max(1, requests_per_window)
        self.win = max(1, window_seconds)
        self.burst = burst if burst is not None else self.rpw
        self._buckets = {}
        self._rate = self.rpw / self.win

    def allow(self, key: str) -> bool:
        now = time.time()
        bucket = self._buckets.get(key)
        if not bucket:
            self._buckets[key] = {"tokens": self.burst - 1, "last": now}
            return True
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self._rate)
        bucket["last"] = now
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        return False

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host
    limiter = getattr(app.state, "rate_limiter", None)
    if limiter and not limiter.allow(client_ip):
        metrics = getattr(app.state, "metrics", None)
        if metrics:
            metrics.rate_limited_count += 1
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests. Please slow down."
            }
        )
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000.0
    metrics = getattr(app.state, "metrics", None)
    if metrics:
        metrics.request_count += 1
        metrics.total_request_ms += duration_ms
    return response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers including CSP to prevent XSS attacks"""
    response = await call_next(request)
    
    # Content Security Policy - prevents XSS attacks
    env_now = os.getenv("ENV", "dev").lower()
    if env_now == "prod":
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://openrouter.ai; "
            "frame-ancestors 'none';"
        )
    else:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' http://localhost:* https://openrouter.ai; "
            "frame-ancestors 'none';"
        )
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Enable XSS protection in legacy browsers
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Enforce HTTPS in production (commented out for local dev)
    # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions policy (formerly Feature-Policy)
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# CORS Configuration - Read from environment variable
# Default to localhost for development, but allow configuration for production
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router)
app.include_router(scans.router)
app.include_router(metrics.router)
app.include_router(reports.router)
app.include_router(comparison.router)
app.include_router(notifications.router)

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")
    # Initialize metrics and rate limiter from environment
    class Metrics:
        def __init__(self):
            self.request_count = 0
            self.rate_limited_count = 0
            self.total_request_ms = 0.0
    app.state.metrics = Metrics()
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", str(RATE_LIMIT_REQUESTS)))
    app.state.rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, RATE_LIMIT_BURST)
    
    # Check scanner dependencies
    logger.info("Checking scanner dependencies...")
    dependency_status = DependencyChecker.check_all_dependencies()
    
    # Store dependency status in Config table
    db = SessionLocal()
    try:
        for tool_name, info in dependency_status.items():
            # Store as JSON in Config table
            config_key = f"scanner_status_{tool_name}"
            config_entry = db.query(Config).filter(Config.key == config_key).first()
            
            if config_entry:
                config_entry.value = json.dumps(info)
            else:
                config_entry = Config(key=config_key, value=json.dumps(info))
                db.add(config_entry)
        
        db.commit()
    finally:
        db.close()
    
    # Print status summary
    DependencyChecker.print_status_summary()
    
    logger.info("Asura API is running on http://localhost:8000")
    logger.info("API Documentation: http://localhost:8000/docs")

@app.get("/")
async def root():
    return {
        "message": "Asura API is running", 
        "version": "0.3.0",
        "status": "healthy"
    }

@app.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe.
    Returns 200 if the application is running (can handle requests).
    This should always return 200 unless the app is completely broken.
    """
    return {
        "status": "alive",
        "service": "Asura API",
        "version": "0.3.0"
    }

@app.get("/health/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe.
    Returns 200 if the application is ready to serve traffic.
    Returns 503 if dependencies are not available.
    """
    from pathlib import Path
    import shutil
    
    # Check critical dependencies
    issues = []
    
    # 1. Database check
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        issues.append(f"Database unavailable: {str(e)}")
    
    # 2. At least one scanner must be available
    dependency_status = DependencyChecker.check_all_dependencies()
    available_scanners = [tool for tool, info in dependency_status.items() if info["available"]]
    
    if len(available_scanners) == 0:
        issues.append("No security scanners available")
    
    # 3. Disk space check
    try:
        disk_usage = shutil.disk_usage(Path.cwd())
        free_gb = disk_usage.free / (1024**3)
        if free_gb < 0.5:  # Less than 500MB
            issues.append(f"Critical disk space: {round(free_gb, 2)}GB free")
    except Exception as e:  # nosec B110
        # Don't fail readiness on disk check - it's a nice-to-have metric
        logger.debug(f"Disk space check failed (non-critical): {e}")
    
    if issues:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "Asura API",
                "issues": issues
            }
        )
    
    return {
        "status": "ready",
        "service": "Asura API",
        "version": "0.3.0",
        "scanners_available": len(available_scanners)
    }

@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Checks:
    - Database connectivity
    - Scanner tool availability
    - Disk space
    - Service status
    
    Returns HTTP 200 if healthy, 503 if degraded/unhealthy
    """
    import shutil
    from pathlib import Path
    
    health_report = {
        "service": "Asura API",
        "version": "0.3.0",
        "status": "healthy",
        "checks": {}
    }
    
    issues = []
    
    # 1. Database connectivity check
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute("SELECT 1")
        db.close()
        health_report["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_report["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        issues.append("Database connection failed")
    
    # 2. Scanner availability check
    dependency_status = DependencyChecker.check_all_dependencies()
    available_scanners = [tool for tool, info in dependency_status.items() if info["available"]]
    total_scanners = len(dependency_status)
    
    scanner_status = "healthy" if len(available_scanners) > 0 else "degraded"
    health_report["checks"]["scanners"] = {
        "status": scanner_status,
        "available": available_scanners,
        "total": total_scanners,
        "message": f"{len(available_scanners)}/{total_scanners} scanners available"
    }
    
    if len(available_scanners) == 0:
        issues.append("No security scanners available")
    
    # 3. Disk space check (require at least 1GB free)
    try:
        current_dir = Path.cwd()
        disk_usage = shutil.disk_usage(current_dir)
        free_gb = disk_usage.free / (1024**3)  # Convert to GB
        total_gb = disk_usage.total / (1024**3)
        used_percent = (disk_usage.used / disk_usage.total) * 100
        
        disk_status = "healthy" if free_gb >= 1.0 else "degraded"
        health_report["checks"]["disk_space"] = {
            "status": disk_status,
            "free_gb": round(free_gb, 2),
            "total_gb": round(total_gb, 2),
            "used_percent": round(used_percent, 2),
            "message": f"{round(free_gb, 2)}GB free"
        }
        
        if free_gb < 1.0:
            issues.append(f"Low disk space: {round(free_gb, 2)}GB free")
        if free_gb < 0.5:
            issues.append("Critical: Less than 500MB disk space remaining")
    except Exception as e:
        health_report["checks"]["disk_space"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    # 4. Determine overall status
    if any(check.get("status") == "unhealthy" for check in health_report["checks"].values()):
        health_report["status"] = "unhealthy"
        health_report["http_code"] = 503
    elif any(check.get("status") == "degraded" for check in health_report["checks"].values()):
        health_report["status"] = "degraded"
        health_report["http_code"] = 200
    else:
        health_report["status"] = "healthy"
        health_report["http_code"] = 200
    
    if issues:
        health_report["issues"] = issues
    
    # Return appropriate HTTP status code
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=health_report,
        status_code=health_report["http_code"]
    )
@app.get("/metrics/internal")
async def internal_metrics():
    metrics = getattr(app.state, "metrics", None)
    if not metrics:
        return {"request_count": 0, "rate_limited_count": 0, "avg_request_ms": 0.0}
    avg_ms = (metrics.total_request_ms / metrics.request_count) if metrics.request_count else 0.0
    return {
        "request_count": metrics.request_count,
        "rate_limited_count": metrics.rate_limited_count,
        "avg_request_ms": round(avg_ms, 2)
    }
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger("asura")
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
