# schemas/poll.py
from pydantic import BaseModel, Field

class PollRequest(BaseModel):
    symbols: list[str] = Field(min_items=1)
    interval: int = Field(gt=0, description="seconds between polls")
    provider: str | None = None 

class PollAcceptedResponse(BaseModel):
    job_id: str
    status: str = Field(default="accepted")
    config: PollRequest