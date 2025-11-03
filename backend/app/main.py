from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.database import init_db
from app.api import projects, scans, metrics, reports, comparison
import time

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

# Rate limiting middleware (simple implementation)
request_times = {}

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """Simple rate limiting: 60 requests per minute per IP"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old entries (older than 60 seconds)
    if client_ip in request_times:
        request_times[client_ip] = [t for t in request_times[client_ip] if current_time - t < 60]
    else:
        request_times[client_ip] = []
    
    # Check rate limit
    if len(request_times[client_ip]) >= 60:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests. Maximum 60 requests per minute."
            }
        )
    
    # Add current request time
    request_times[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized")
    print("🚀 Asura API is running on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")

@app.get("/")
async def root():
    return {
        "message": "Asura API is running", 
        "version": "0.3.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Asura API"}
