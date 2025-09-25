from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel
import os
import uuid
import asyncio
from .worker import enqueue_job

app = FastAPI()

AGENT_SECRET = os.environ.get("AGENT_SECRET")


class GitHubEvent(BaseModel):
    action: str = None
    pull_request: dict = None


@app.post("/webhook")
async def webhook(request: Request, x_hub_signature: str | None = Header(None)):
    # Very small auth: expect AGENT_SECRET in header X-Agent-Secret
    agent_secret = request.headers.get("X-Agent-Secret")
    if AGENT_SECRET and agent_secret != AGENT_SECRET:
        raise HTTPException(status_code=401, detail="invalid agent secret")

    payload = await request.json()
    # Minimal validation - accept PR opened/edited/synchronize
    event = GitHubEvent(**payload)

    # Enqueue job for analysis
    job_id = str(uuid.uuid4())
    await enqueue_job({"id": job_id, "payload": payload})

    return {"status": "accepted", "job_id": job_id}


@app.get("/health")
async def health():
    return {"status": "ok"}
