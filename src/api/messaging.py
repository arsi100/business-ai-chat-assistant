from enum import Enum
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from twilio.rest import Client
import httpx
from ..config import get_settings

class MessageProvider(ABC):
    @abstractmethod
    async def send_message(self, to: str, message: str, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

class TwilioProvider(MessageProvider):
    def __init__(self):
        settings = get_settings()
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        # Always use the sandbox number format
        self.from_number = f"whatsapp:+14155238886"  # Hardcode the sandbox number for testing
        print(f"Initialized TwilioProvider with number: {self.from_number}")  # Debug print

    async def send_message(self, to: str, message: str, **kwargs) -> Dict[str, Any]:
        try:
            # Ensure WhatsApp format for to_number
            to_number = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
            
            print(f"\nDebug Info:")
            print(f"From Number: {self.from_number}")
            print(f"To Number: {to_number}")
            print(f"Message: {message}\n")
            
            response = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=to_number
            )
            print(f"Message sent successfully: {response.sid}")
            return {"message_id": response.sid, "status": response.status}
        except Exception as e:
            print(f"Error details: {str(e)}")
            raise

    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "from": payload.get("From", "").replace("whatsapp:", ""),
            "message": payload.get("Body", ""),
            "message_id": payload.get("MessageSid", ""),
            "timestamp": payload.get("DateCreated", "")
        }

# Keep your existing Meta provider
class MetaProvider(MessageProvider):
    def __init__(self):
        settings = get_settings()
        self.token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/v17.0"

    # Your existing Meta implementation... 