"""
External communication platforms for Terry Delmonaco Automation Agent.
Provides integration with Google Chat and Signal for agent communication.
"""

import asyncio
import json
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

from ..utils.logger import LoggerMixin


class BaseCommunicationClient(LoggerMixin):
    """Base class for external communication platforms."""
    
    def __init__(self, platform_name: str):
        super().__init__()
        self.platform_name = platform_name
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Connect to the communication platform."""
        raise NotImplementedError
    
    async def disconnect(self):
        """Disconnect from the communication platform."""
        self.is_connected = False
        self.log_info(f"Disconnected from {self.platform_name}")
    
    async def send_message(self, recipient: str, message: str) -> bool:
        """Send message to recipient."""
        raise NotImplementedError
    
    async def receive_messages(self) -> List[Dict[str, Any]]:
        """Receive messages from the platform."""
        raise NotImplementedError
    
    async def is_healthy(self) -> bool:
        """Check if the connection is healthy."""
        return self.is_connected


class GoogleChatClient(BaseCommunicationClient):
    """Google Chat integration for team communication."""
    
    def __init__(self):
        super().__init__("Google Chat")
        self.api_key = os.getenv("GOOGLE_CHAT_API_KEY")
        self.webhook_url = os.getenv("GOOGLE_CHAT_WEBHOOK_URL")
        self.session = None
    
    async def connect(self) -> bool:
        """Connect to Google Chat API."""
        try:
            if not self.api_key:
                self.log_warning("Google Chat API key not configured")
                return False
            
            self.session = aiohttp.ClientSession()
            self.is_connected = True
            self.log_info("Connected to Google Chat")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to connect to Google Chat: {e}")
            return False
    
    async def send_message(self, recipient: str, message: str) -> bool:
        """Send message to Google Chat space or user."""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Google Chat message format
            chat_message = {
                "text": message,
                "cards": [{
                    "header": {
                        "title": "Terry Delmonaco Agent",
                        "subtitle": f"Message from {self.platform_name}"
                    },
                    "sections": [{
                        "widgets": [{
                            "textParagraph": {
                                "text": message
                            }
                        }]
                    }]
                }]
            }
            
            # Send to webhook or specific space
            if self.webhook_url:
                async with self.session.post(
                    self.webhook_url,
                    json=chat_message,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        self.log_info(f"Message sent to Google Chat: {recipient}")
                        return True
                    else:
                        self.log_error(f"Failed to send Google Chat message: {response.status}")
                        return False
            else:
                self.log_warning("Google Chat webhook URL not configured")
                return False
                
        except Exception as e:
            self.log_error(f"Error sending Google Chat message: {e}")
            return False
    
    async def receive_messages(self) -> List[Dict[str, Any]]:
        """Receive messages from Google Chat (webhook endpoint)."""
        # This would be implemented as a webhook endpoint
        # For now, return empty list
        return []
    
    async def disconnect(self):
        """Disconnect from Google Chat."""
        if self.session:
            await self.session.close()
        await super().disconnect()


class SignalClient(BaseCommunicationClient):
    """Signal integration for secure messaging."""
    
    def __init__(self):
        super().__init__("Signal")
        self.signal_cli_path = os.getenv("SIGNAL_CLI_PATH", "signal-cli")
        self.phone_number = os.getenv("SIGNAL_PHONE_NUMBER")
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Connect to Signal CLI."""
        try:
            if not self.phone_number:
                self.log_warning("Signal phone number not configured")
                return False
            
            # Check if signal-cli is available
            process = await asyncio.create_subprocess_exec(
                self.signal_cli_path, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if process.returncode == 0:
                self.is_connected = True
                self.log_info("Connected to Signal CLI")
                return True
            else:
                self.log_error("Signal CLI not available")
                return False
                
        except Exception as e:
            self.log_error(f"Failed to connect to Signal: {e}")
            return False
    
    async def send_message(self, recipient: str, message: str) -> bool:
        """Send message via Signal."""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Use signal-cli to send message
            process = await asyncio.create_subprocess_exec(
                self.signal_cli_path,
                "-a", self.phone_number,
                "send",
                "-m", message,
                recipient,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                self.log_info(f"Signal message sent to {recipient}")
                return True
            else:
                self.log_error(f"Failed to send Signal message: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.log_error(f"Error sending Signal message: {e}")
            return False
    
    async def receive_messages(self) -> List[Dict[str, Any]]:
        """Receive messages from Signal."""
        try:
            # Use signal-cli to receive messages
            process = await asyncio.create_subprocess_exec(
                self.signal_cli_path,
                "-a", self.phone_number,
                "receive",
                "--json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                messages = []
                for line in stdout.decode().splitlines():
                    if line.strip():
                        try:
                            message_data = json.loads(line)
                            messages.append(message_data)
                        except json.JSONDecodeError:
                            continue
                return messages
            else:
                self.log_error(f"Failed to receive Signal messages: {stderr.decode()}")
                return []
                
        except Exception as e:
            self.log_error(f"Error receiving Signal messages: {e}")
            return []
    
    async def disconnect(self):
        """Disconnect from Signal."""
        await super().disconnect()


class CommunicationManager(LoggerMixin):
    """Manager for all external communication platforms."""
    
    def __init__(self):
        super().__init__()
        self.clients = {}
        self.message_queue = asyncio.Queue()
        self.is_running = False
    
    async def initialize(self):
        """Initialize all communication clients."""
        try:
            # Initialize Google Chat
            google_chat = GoogleChatClient()
            if await google_chat.connect():
                self.clients['google_chat'] = google_chat
            
            # Initialize Signal
            signal = SignalClient()
            if await signal.connect():
                self.clients['signal'] = signal
            
            self.log_info(f"Initialized {len(self.clients)} communication clients")
            
        except Exception as e:
            self.log_error(f"Failed to initialize communication manager: {e}")
    
    async def send_message(self, platform: str, recipient: str, message: str) -> bool:
        """Send message via specified platform."""
        if platform not in self.clients:
            self.log_error(f"Unsupported platform: {platform}")
            return False
        
        client = self.clients[platform]
        return await client.send_message(recipient, message)
    
    async def broadcast_message(self, message: str, platforms: List[str] = None) -> Dict[str, bool]:
        """Broadcast message to multiple platforms."""
        if platforms is None:
            platforms = list(self.clients.keys())
        
        results = {}
        for platform in platforms:
            if platform in self.clients:
                # For broadcast, we might use a default recipient or group
                recipient = self._get_broadcast_recipient(platform)
                results[platform] = await self.send_message(platform, recipient, message)
            else:
                results[platform] = False
        
        return results
    
    def _get_broadcast_recipient(self, platform: str) -> str:
        """Get default broadcast recipient for platform."""
        if platform == "google_chat":
            return os.getenv("GOOGLE_CHAT_SPACE_ID", "default_space")
        elif platform == "signal":
            return os.getenv("SIGNAL_GROUP_ID", "default_group")
        else:
            return "default"
    
    async def receive_all_messages(self) -> Dict[str, List[Dict[str, Any]]]:
        """Receive messages from all platforms."""
        messages = {}
        for platform, client in self.clients.items():
            try:
                messages[platform] = await client.receive_messages()
            except Exception as e:
                self.log_error(f"Error receiving messages from {platform}: {e}")
                messages[platform] = []
        
        return messages
    
    async def start_message_processing(self):
        """Start processing incoming messages."""
        self.is_running = True
        self.log_info("Started message processing")
        
        while self.is_running:
            try:
                # Receive messages from all platforms
                all_messages = await self.receive_all_messages()
                
                for platform, messages in all_messages.items():
                    for message in messages:
                        await self._process_message(platform, message)
                
                await asyncio.sleep(5)  # Check for messages every 5 seconds
                
            except Exception as e:
                self.log_error(f"Message processing error: {e}")
                await asyncio.sleep(10)
    
    async def _process_message(self, platform: str, message: Dict[str, Any]):
        """Process incoming message."""
        try:
            # Extract message content
            content = self._extract_message_content(platform, message)
            sender = self._extract_sender(platform, message)
            
            if content and sender:
                # Add to processing queue
                await self.message_queue.put({
                    "platform": platform,
                    "sender": sender,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    "raw_message": message
                })
                
                self.log_info(f"Queued message from {sender} via {platform}")
                
        except Exception as e:
            self.log_error(f"Error processing message from {platform}: {e}")
    
    def _extract_message_content(self, platform: str, message: Dict[str, Any]) -> Optional[str]:
        """Extract message content based on platform."""
        if platform == "google_chat":
            return message.get("text", "")
        elif platform == "signal":
            return message.get("envelope", {}).get("dataMessage", {}).get("message", "")
        else:
            return str(message)
    
    def _extract_sender(self, platform: str, message: Dict[str, Any]) -> Optional[str]:
        """Extract sender information based on platform."""
        if platform == "google_chat":
            return message.get("user", {}).get("displayName", "Unknown")
        elif platform == "signal":
            return message.get("envelope", {}).get("source", "Unknown")
        else:
            return "Unknown"
    
    async def get_message(self) -> Optional[Dict[str, Any]]:
        """Get next message from queue."""
        try:
            return await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None
    
    async def shutdown(self):
        """Shutdown communication manager."""
        self.is_running = False
        
        for platform, client in self.clients.items():
            try:
                await client.disconnect()
            except Exception as e:
                self.log_error(f"Error disconnecting from {platform}: {e}")
        
        self.log_info("Communication manager shutdown complete") 
