import time
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.common import Message

router = APIRouter(prefix="/leads")

_rate_limits: dict[str, list[float]] = defaultdict(list)
WINDOW = 60
LIMIT = 5


@router.post("/", response_model=Message)
async def create_lead(request: Request) -> Message:
    client_ip = request.client.host if request.client else "anon"
    now = time.time()
    timestamps = _rate_limits[client_ip]
    timestamps[:] = [ts for ts in timestamps if now - ts < WINDOW]
    if len(timestamps) >= LIMIT:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many leads")
    timestamps.append(now)
    return Message(message="received")
