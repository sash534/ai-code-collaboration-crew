from datetime import datetime, timezone
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Slack Mock Service", version="1.0.0")

messages: list[dict] = []
channels = [
    {"id": "C001", "name": "incident-response", "topic": "Production incident coordination"},
    {"id": "C002", "name": "engineering", "topic": "General engineering discussion"},
    {"id": "C003", "name": "on-call", "topic": "On-call alerts and escalations"},
    {"id": "C004", "name": "platform-alerts", "topic": "Automated platform alerts"},
]


class SendMessageRequest(BaseModel):
    channel: str
    text: str
    username: str = "incident-bot"
    icon_emoji: str = ":rotating_light:"
    blocks: Optional[list[dict]] = None


@app.post("/api/messages")
async def send_message(req: SendMessageRequest):
    msg = {
        "id": f"msg-{len(messages)+1:04d}",
        "channel": req.channel,
        "text": req.text,
        "username": req.username,
        "icon_emoji": req.icon_emoji,
        "blocks": req.blocks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ok": True,
    }
    messages.append(msg)
    return msg


@app.get("/api/messages")
async def get_messages(channel: Optional[str] = None, limit: int = 50):
    filtered = messages
    if channel:
        filtered = [m for m in messages if m["channel"] == channel]
    return {"results": filtered[-limit:], "total": len(filtered)}


@app.get("/api/channels")
async def list_channels():
    return {"results": channels, "total": len(channels)}


@app.get("/api/health")
async def health():
    return {"status": "ok", "messages_count": len(messages)}
