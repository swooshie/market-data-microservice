from fastapi import FastAPI, HTTPException, Request, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


def add_rate_limiting(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(HTTPException, _rate_limit_exceeded_handler)
