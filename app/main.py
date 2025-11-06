import logging
import os
from fastapi import FastAPI
from .api import router as api
from .middleware import RequestLoggingMiddleware, ErrorFormattingMiddleware
from .rate_limit import RateLimitMiddleware
from .metrics import router as metrics_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="AI Project API",
    version="0.1.20",
    description="API with request logging, rate limiting, and metrics",
)

# Add middleware (order matters - first added is outermost)
app.add_middleware(ErrorFormattingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Use higher rate limit for testing
is_testing = os.getenv("TESTING", "false").lower() == "true"
rate_limit = 1000 if is_testing else 60

app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=rate_limit,
    burst_size=10,
)

# Include routers
app.include_router(api, prefix="/api")
app.include_router(metrics_router, prefix="/api")
