import uuid
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.app.core.context import set_request_id

REQUEST_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")

class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID")
        if not req_id or not REQUEST_ID_REGEX.match(req_id):
            req_id = str(uuid.uuid4())
            
        set_request_id(req_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response
