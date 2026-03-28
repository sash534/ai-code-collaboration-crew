from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
from src.services.client import ServiceClient


class SendMessageInput(BaseModel):
    channel: str = Field(..., description="Channel name to send message to (e.g. 'incident-response')")
    text: str = Field(..., description="Message text. For incidents, include severity, service, summary, and action items.")


class SlackSendMessageTool(BaseTool):
    name: str = "send_slack_message"
    description: str = "Send a notification message to a Slack channel. Use channel 'incident-response' for incident alerts. Include severity, affected service, impact summary, and current status."
    args_schema: type[BaseModel] = SendMessageInput

    def _run(self, channel: str, text: str) -> str:
        client = ServiceClient("slack")
        result = client.post(
            "/messages",
            channel=channel,
            text=text,
            username="incident-bot",
            icon_emoji=":rotating_light:",
        )
        return json.dumps(result, indent=2)


class SlackListChannelsTool(BaseTool):
    name: str = "list_slack_channels"
    description: str = "List available Slack channels to determine where to send notifications."

    def _run(self) -> str:
        client = ServiceClient("slack")
        result = client.get("/channels")
        return json.dumps(result, indent=2)
