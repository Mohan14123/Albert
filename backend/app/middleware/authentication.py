from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.security import verify_access_token
from app.core.exceptions import AuthenticationError

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract JWT token, verify it, and attach user_id to request state.
    Note: Real user DB fetch is handled by `get_current_user` dependency for endpoints
    that explicitly require a user. This middleware is purely for context (e.g., logging).
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Default state
        request.state.user_id = None
        
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                user_id = verify_access_token(token)
                request.state.user_id = user_id
            except AuthenticationError:
                # We don't block the request here because some endpoints might be public.
                # The `get_current_user` dependency will block if authentication is required.
                pass
                
        response = await call_next(request)
        return response
