"""
Slack Message Listener Tool for Donna RAG Assistant

This module provides functionality to listen to Slack messages, process them,
and respond using the RAG pipeline. It supports both lookup and publish intents.

Based on the reference implementation from RAG_2nd_iteration/notebooks/main.ipynb
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Set, Optional, Callable, Any
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from utils.secrets_loader import load_secrets


class SlackListener:
    """
    Slack message listener and processor for Donna RAG Assistant.
    
    Handles Slack events, processes user queries, and manages bot responses
    for both data lookup and dataset publishing operations.
    """
    
    def __init__(self, 
                 allowed_channels: Optional[List[str]] = None,
                 query_processor: Optional[Callable] = None,
                 publish_handler: Optional[Callable] = None,
                 file_handler: Optional[Callable] = None):
        """
        Initialize the Slack listener.
        
        Args:
            allowed_channels: List of channel IDs where bot should respond
            query_processor: Function to process lookup queries
            publish_handler: Function to handle publish requests
        """
        secrets = load_secrets()

        self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_app_token = os.getenv("SLACK_APP_TOKEN")
        self.bot_user_id = os.getenv("BOT_USER_ID")

        if not all([self.slack_bot_token, self.slack_app_token, self.bot_user_id]):
            raise ValueError("Missing Slack credentials")

        self.app = App(token=self.slack_bot_token)
        
        # Configuration
        self.allowed_channels = allowed_channels or []
        self.query_processor = query_processor
        self.publish_handler = publish_handler
        self.file_handler = file_handler
        
        # Deduplication tracking
        self.seen_events: Set[tuple] = set()
        
        # Register event handlers
        self._register_handlers()
        
    def _register_handlers(self) -> None:
        """Register Slack event handlers."""
        @self.app.event("message")
        @self.app.event("app_mention")
        def handle_message(event, say):
            self._handle_message_event(event, say)
        @self.app.event("file_shared")
        def handle_file(event, say):
            self._handle_file_shared_event(event, say)
    
    def _handle_message_event(self, event: Dict[str, Any], say: Callable) -> None:
        """
        Handle incoming Slack message events.
        """
        print("\n📩 Incoming Slack event:")
        try:
            print(json.dumps(event, indent=2))
        except Exception:
            print(event)
    
        # Ignore bot messages
        if event.get("subtype") == "bot_message":
            print("🤖 Ignored a bot_message event")
            return
    
        # Check if channel is allowed
        channel_id = event.get("channel", "")
        if self.allowed_channels and channel_id not in self.allowed_channels:
            print(f"⚠ Ignored message from disallowed channel {channel_id}")
            return
    
        # Check for duplicates
        if self._is_duplicate_event(event):
            print(f"⚠ Duplicate event ignored: {event.get('ts')}")
            return
    
        print(f"✅ Processing new event {event.get('ts')} with text: {event.get('text')}")
    
        # Extract message details
        text = event.get("text", "")
        ts = event.get("ts")
        thread_ts = event.get("ts") or event.get("event_ts")
    
        # Check if bot is mentioned
        bot_mention = f"<@{self.bot_user_id}>"
        if bot_mention not in text:
            print(f"ℹ Bot mention ({bot_mention}) not found in text: {text}")
            return
    
        # Process the message
        try:
            self._process_user_query(event, say, channel_id, thread_ts)
        except Exception as e:
            error_msg = f"⚠ Error processing message: {str(e)}"
            print(error_msg)
            say(text=error_msg, thread_ts=thread_ts)

    
    def _is_duplicate_event(self, event: Dict[str, Any]) -> bool:
        """
        Check if event has already been processed.
        
        Args:
            event: Slack event data
            
        Returns:
            True if event is duplicate, False otherwise
        """
        key = (event.get("channel"), event.get("ts"), event.get("text"))
        if key in self.seen_events:
            return True
        self.seen_events.add(key)
        return False
    
    def _extract_user_query(self, event: Dict[str, Any]) -> str:
        """
        Extract and clean user query from event.
        
        Args:
            event: Slack event data
            
        Returns:
            Cleaned user query text
        """
        text = event.get("text", "")
        bot_mention = f"<@{self.bot_user_id}>"
        cleaned_text = text.replace(bot_mention, "").strip()
        return cleaned_text
    
    def _process_user_query(self, event: Dict[str, Any], say: Callable, 
                           channel_id: str, thread_ts: str) -> None:
        """
        Process user query and respond appropriately.
        
        Args:
            event: Slack event data
            say: Slack response function
            channel_id: Slack channel ID
            thread_ts: Thread timestamp for responses
        """
        user_query = self._extract_user_query(event)
        print(f"\n user_query: {user_query}")
        
        # If no query processor is available, respond with error
        if not self.query_processor:
            say(text="⚠ Query processor not configured", thread_ts=thread_ts)
            return
        
        # Process query through external handler
        try:
            result = self.query_processor(user_query, self.app.client, channel_id, thread_ts)
            
            # Send response based on result
            if isinstance(result, dict) and result.get("success"):
                if result.get("response"):
                    say(text=result["response"], thread_ts=thread_ts)
            else:
                error_msg = result.get("error", "Unknown error occurred")
                say(text=f"⚠ {error_msg}", thread_ts=thread_ts)
                
        except Exception as e:
            say(text=f"⚠ Processing failed: {str(e)}", thread_ts=thread_ts)
    
    def format_event_debug(self, event: Dict[str, Any]) -> str:
        """
        Format event for debugging purposes.
        
        Args:
            event: Slack event data
            
        Returns:
            Formatted debug string
        """
        channel_id = event.get("channel", "")
        ts = event.get("ts", "")
        thread_ts = event.get("thread_ts", "")
        text = event.get("text", "")
        
        lines = [
            f"\n Event received at {time.strftime('%X')}",
            json.dumps(event, indent=2),
            f"Channel: {channel_id}, ts: {ts}, thread_ts: {thread_ts}",
            f"User: {event.get('user')}, Text: {text}\n"
        ]
        return "\n".join(lines)
    
    def start_listening(self) -> None:
        """Start the Slack bot in socket mode."""
        print("🤖 Slack bot is starting...")
        handler = SocketModeHandler(self.app, self.slack_app_token)
        handler.start()
    
    def add_allowed_channel(self, channel_id: str) -> None:
        """Add a channel to the allowed channels list."""
        if channel_id not in self.allowed_channels:
            self.allowed_channels.append(channel_id)
    
    def remove_allowed_channel(self, channel_id: str) -> None:
        """Remove a channel from the allowed channels list."""
        if channel_id in self.allowed_channels:
            self.allowed_channels.remove(channel_id)
    
    def set_query_processor(self, processor: Callable) -> None:
        """Set the query processing function."""
        self.query_processor = processor
    
    def set_publish_handler(self, handler: Callable) -> None:
        """Set the publish handling function."""
        self.publish_handler = handler
    
    def get_bot_info(self) -> Dict[str, str]:
        """Get bot configuration information."""
        return {
            "bot_user_id": self.bot_user_id,
            "allowed_channels": self.allowed_channels,
            "has_query_processor": self.query_processor is not None,
            "has_publish_handler": self.publish_handler is not None
        }

    def _handle_file_shared_event(self, event: Dict[str, Any], say: Callable) -> None:
        try:
            file_id = event.get("file", {}).get("id")
            file_name = event.get("file", {}).get("name")
            file_type = event.get("file", {}).get("filetype")

            if not file_id or not file_name:
                return

            file_info = self.app.client.files_info(file=file_id)
            url_private = file_info["file"]["url_private_download"]

            print(f"📎 File metadata captured: {file_name} ({file_type})")
            # just pass metadata now
            if self.file_handler:
                self.file_handler(file_name, file_type, url_private, file_info["file"], self.app.client)

            say(text=f"📥 File metadata captured: *{file_name}*", thread_ts=event.get("ts") or event.get("event_ts"))

        except Exception as e:
            error_msg = f"⚠ Error handling file metadata: {str(e)}"
            print(error_msg)
            say(text=error_msg, thread_ts=event.get("ts") or event.get("event_ts"))

    










