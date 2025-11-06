"""Rate limiting middleware."""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter.

    For production, use Redis-based rate limiting like slowapi.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        # Store: {client_ip: [(timestamp, count), ...]}
        self._buckets: Dict[str, list[Tuple[float, int]]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for proxy headers first
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        if request.client:
            return request.client.host

        return "unknown"

    def _clean_old_requests(self, client_ip: str, current_time: float):
        """Remove requests older than 1 minute."""
        cutoff_time = current_time - 60
        self._buckets[client_ip] = [
            (ts, count) for ts, count in self._buckets[client_ip] if ts > cutoff_time
        ]

    def _is_rate_limited(self, client_ip: str) -> Tuple[bool, int]:
        """
        Check if client should be rate limited.

        Returns (is_limited, requests_made).
        """
        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(client_ip, current_time)

        # Count recent requests
        recent_requests = sum(count for _, count in self._buckets[client_ip])

        # Check rate limit
        if recent_requests >= self.requests_per_minute:
            return True, recent_requests

        # Add current request
        self._buckets[client_ip].append((current_time, 1))

        return False, recent_requests + 1

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for health and metrics endpoints
        skip_paths = ["/api/health", "/api/metrics", "/api/version"]
        if request.url.path in skip_paths:
            response = await call_next(request)
            # Still add headers for consistency
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(self.requests_per_minute)
            return response

        client_ip = self._get_client_ip(request)
        is_limited, request_count = self._is_rate_limited(client_ip)

        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate Limit Exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_minute} requests per minute.",
                    "retry_after": 60,
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = max(0, self.requests_per_minute - request_count)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
