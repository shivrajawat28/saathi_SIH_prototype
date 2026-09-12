"""
SAATHI Server-Side Rate Limiter Module
Thread-safe sliding window rate limiting for authentication and high-computation ML endpoints.
Zero external dependencies, fast in-memory execution with automatic periodic bucket cleanup.
"""

import time
import threading
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status

class SlidingWindowRateLimiter:
    def __init__(self):
        self._requests: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.time()

    def _cleanup(self, now: float, window_seconds: float):
        """Purge stale timestamps to prevent unbounded memory growth."""
        if now - self._last_cleanup < 60:
            return
        self._last_cleanup = now
        stale_keys = []
        for key, timestamps in list(self._requests.items()):
            valid_ts = [ts for ts in timestamps if now - ts < window_seconds * 2]
            if not valid_ts:
                stale_keys.append(key)
            else:
                self._requests[key] = valid_ts
        for k in stale_keys:
            self._requests.pop(k, None)

    def check_rate_limit(
        self,
        key: str,
        max_requests: int = 10,
        window_seconds: int = 60
    ) -> Tuple[bool, int, float]:
        """
        Check if a client identified by `key` has exceeded `max_requests` in `window_seconds`.
        Returns (is_allowed, remaining_requests, retry_after_seconds).
        """
        now = time.time()
        with self._lock:
            self._cleanup(now, window_seconds)
            timestamps = self._requests.get(key, [])
            
            # Filter timestamps within current window
            valid_timestamps = [ts for ts in timestamps if now - ts < window_seconds]
            
            if len(valid_timestamps) >= max_requests:
                earliest = valid_timestamps[0]
                retry_after = max(1, int(window_seconds - (now - earliest)))
                return False, 0, retry_after

            valid_timestamps.append(now)
            self._requests[key] = valid_timestamps
            remaining = max(0, max_requests - len(valid_timestamps))
            return True, remaining, 0.0

rate_limiter = SlidingWindowRateLimiter()

def rate_limit(max_requests: int = 15, window_seconds: int = 60):
    """
    FastAPI dependency enforcing sliding window rate limit per client IP.
    """
    async def dependency(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        endpoint = request.url.path
        rate_key = f"{client_ip}:{endpoint}"
        
        is_allowed, remaining, retry_after = rate_limiter.check_rate_limit(
            key=rate_key,
            max_requests=max_requests,
            window_seconds=window_seconds
        )
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Too many requests. Please retry in {int(retry_after)} seconds.",
                headers={"Retry-After": str(int(retry_after))}
            )
    return dependency
