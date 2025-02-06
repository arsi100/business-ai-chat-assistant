from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Force reload of environment variables
load_dotenv(find_dotenv(), override=True)

class Settings(BaseSettings):
    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent
    
    # API Keys
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str = "your_pinecone_api_key"  # Remove default if exists
    PINECONE_ENVIRONMENT: str = "us-east-1"  # Make sure this matches your env
    WHATSAPP_API_TOKEN: str
    
    # AI Settings
    MODEL_NAME: str = "gpt-3.5-turbo"
    MAX_TOKENS: int = 500
    TEMPERATURE: float = 0.7
    
    # Vector DB Settings
    PINECONE_INDEX_NAME: str = "whatsapp-bot"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database URL
    DATABASE_URL: str
    
    # WhatsApp settings
    WHATSAPP_PHONE_NUMBER_ID: str
    
    # Twilio settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_NUMBER: str
    
    # Provider selection
    WHATSAPP_PROVIDER: str = "twilio"  # or "meta"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    # Clear the LRU cache to ensure fresh settings
    get_settings.cache_clear()
    return Settings() 