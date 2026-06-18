import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.services.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

AUTH_PATHS = ["/api/v1/auth/login", "/api/v1/auth/refresh"]
MONITORING_PATHS = ["/api/v1/monitoring"]


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.rate_limit_enabled:
            return await call_next(request)

        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        if path in AUTH_PATHS:
            max_r = settings.rate_limit_auth_max
            window = settings.rate_limit_auth_window
            key = f"rl:auth:{client_ip}"
        elif path.startswith("/api/v1/monitoring"):
            max_r = settings.rate_limit_monitoring_max
            window = settings.rate_limit_monitoring_window
            key = f"rl:monitoring:{client_ip}"
        elif path.startswith("/api/v1/"):
            max_r = settings.rate_limit_api_max
            window = settings.rate_limit_api_window
            key = f"rl:api:{client_ip}"
        else:
            return await call_next(request)

        limited, remaining = await rate_limiter.is_rate_limited(key, max_r, window)
        if limited:
            logger.warning(f"Rate limited: {client_ip} -> {path}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests", "retry_after": window},
                headers={"Retry-After": str(window)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
