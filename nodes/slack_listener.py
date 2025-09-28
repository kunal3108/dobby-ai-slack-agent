# nodes/slack_listener.py
import json, time, signal, sys
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from utils.aws_secrets import load_secrets
from typing import Dict, Any
from state import State

class SlackListenerNode:
    """
    LangGraph-compatible Slack listener node.
    It converts Slack events -> State, invokes the workflow,
    and posts responses back to Slack.
    """
    def __init__(self, workflow, allowed_channels=None):
        try:
            secrets = load_secrets()
        except Exception as e:
            raise RuntimeError(f"Failed to load secrets from AWS: {e}")

        self.slack_bot_token = secrets.get("SLACK_BOT_TOKEN")
        self.slack_app_token = secrets.get("SLACK_APP_TOKEN")
        self.bot_user_id = secrets.get("BOT_USER_ID")

        if not all([self.slack_bot_token, self.slack_app_token, self.bot_user_id]):
            raise ValueError("Missing Slack credentials from AWS Secrets Manager")

        self.app = App(token=self.slack_bot_token)
        self.allowed_channels = allowed_channels or []
        self.workflow = workflow  # LangGraph workflow

        self._register_handlers()

    def _register_handlers(self):
        @self.app.event("message")
        @self.app.event("app_mention")
        def handle_message(event, say):
            self._handle_message_event(event, say)

        @self.app.event("file_shared")
        def handle_file(event, say):
            self._handle_file_shared_event(event, say)

    def _is_duplicate(self, event: Dict[str, Any], seen=set()):
        key = (event.get("channel"), event.get("ts"), event.get("text"))
        if key in seen: return True
        seen.add(key)
        return False

    def _extract_user_query(self, event: Dict[str, Any]) -> str:
        text = event.get("text", "")
        bot_mention = f"<@{self.bot_user_id}>"
        return text.replace(bot_mention, "").strip()

    def _handle_message_event(self, event: Dict[str, Any], say):
        if event.get("subtype") == "bot_message": return
        if self.allowed_channels and event.get("channel") not in self.allowed_channels: return
        if self._is_duplicate(event): return

        user_query = self._extract_user_query(event)
        state: State = {
            "text": user_query,
            "channel_id": event["channel"],
            "thread_ts": event.get("ts") or event.get("event_ts"),
        }

        # Invoke LangGraph workflow
        result = self.workflow.invoke(state)

        if result.get("response"):
            say(text=result["response"], thread_ts=state["thread_ts"])

    def _handle_file_shared_event(self, event: Dict[str, Any], say):
        try:
            file_id = event.get("file", {}).get("id")
            file_info = self.app.client.files_info(file=file_id)
            file_meta = file_info["file"]

            state: State = {
                "file_metadata": file_meta,
                "channel_id": event.get("channel"),
                "thread_ts": event.get("ts") or event.get("event_ts"),
            }

            result = self.workflow.invoke(state)
            if result.get("response"):
                say(text=result["response"], thread_ts=state["thread_ts"])

        except Exception as e:
            say(text=f"⚠ File handling error: {str(e)}", thread_ts=event.get("ts"))

    def start(self):
        print("🤖 Slack bot is starting via LangGraph...")
        handler = SocketModeHandler(self.app, self.slack_app_token)
        handler.start()

def shutdown_handler(signum, frame):
    print("🛑 Shutting down SlackListener...")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)
