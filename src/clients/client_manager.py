from typing import Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path

class ClientSettings(BaseModel):
    """Client-specific settings"""
    client_id: str
    whatsapp_number: str
    active: bool = True
    max_tokens: int = 500
    temperature: float = 0.7
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    custom_instructions: Optional[str] = None
    allowed_file_types: List[str] = [".txt", ".pdf", ".csv", ".json"]

class ClientManager:
    def __init__(self):
        self.clients: Dict[str, ClientSettings] = {}
        self.data_file = Path("data/clients.json")
        self._load_clients()
    
    def _load_clients(self) -> None:
        """Load clients from JSON file"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.data_file.exists():
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.clients = {
                        client_id: ClientSettings(**settings)
                        for client_id, settings in data.items()
                    }
            except Exception as e:
                print(f"Error loading clients: {e}")
                self.clients = {}
    
    def _save_clients(self) -> None:
        """Save clients to JSON file"""
        try:
            with open(self.data_file, "w") as f:
                json.dump(
                    {
                        client_id: client.dict()
                        for client_id, client in self.clients.items()
                    },
                    f,
                    default=str,
                    indent=2
                )
        except Exception as e:
            print(f"Error saving clients: {e}")
    
    async def create_client(
        self,
        client_id: str,
        whatsapp_number: str,
        custom_instructions: Optional[str] = None
    ) -> ClientSettings:
        """Create a new client"""
        if client_id in self.clients:
            raise ValueError(f"Client {client_id} already exists")
        
        client = ClientSettings(
            client_id=client_id,
            whatsapp_number=whatsapp_number,
            custom_instructions=custom_instructions
        )
        
        self.clients[client_id] = client
        self._save_clients()
        return client
    
    async def get_client(self, client_id: str) -> Optional[ClientSettings]:
        """Get client settings"""
        return self.clients.get(client_id)
    
    async def update_client(
        self,
        client_id: str,
        whatsapp_number: Optional[str] = None,
        active: Optional[bool] = None,
        custom_instructions: Optional[str] = None,
        **kwargs
    ) -> ClientSettings:
        """Update client settings"""
        if client_id not in self.clients:
            raise ValueError(f"Client {client_id} not found")
        
        client = self.clients[client_id]
        
        update_data = {
            k: v for k, v in {
                "whatsapp_number": whatsapp_number,
                "active": active,
                "custom_instructions": custom_instructions,
                **kwargs
            }.items()
            if v is not None
        }
        
        updated_client = client.copy(update=update_data)
        updated_client.updated_at = datetime.now()
        
        self.clients[client_id] = updated_client
        self._save_clients()
        return updated_client
    
    async def delete_client(self, client_id: str) -> None:
        """Delete a client"""
        if client_id not in self.clients:
            raise ValueError(f"Client {client_id} not found")
        
        del self.clients[client_id]
        self._save_clients()

# Singleton instance
client_manager: ClientManager = None

def get_client_manager() -> ClientManager:
    """Get or create client manager instance"""
    global client_manager
    if client_manager is None:
        client_manager = ClientManager()
    return client_manager 