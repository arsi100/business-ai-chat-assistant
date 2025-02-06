import sys
from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv
import asyncio

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Debug prints
print("Config file location:", find_dotenv())
print("Current directory:", os.getcwd())

# Force reload of .env file
load_dotenv(find_dotenv(), override=True)

# Print environment variables
env_vars = os.environ
print(f"\nEnvironment variables:")
print(f"DATABASE_URL={env_vars.get('DATABASE_URL', '')[:15]}...")
print(f"OPENAI_API_KEY={env_vars.get('OPENAI_API_KEY', '')[:10]}...")
print(f"PINECONE_API_KEY={env_vars.get('PINECONE_API_KEY', '')[:10]}...")
print(f"PINECONE_ENVIRONMENT={env_vars.get('PINECONE_ENVIRONMENT', '')}...")
print(f"WHATSAPP_API_TOKEN={env_vars.get('WHATSAPP_API_TOKEN', '')[:10]}...")

from src.config import get_settings
from src.database.vector_store import get_vector_store
from openai import OpenAI
from pinecone import Pinecone

async def test_vector_store():
    """Test storing and searching embeddings in Pinecone"""
    settings = get_settings()
    
    # Debug: Print Pinecone settings
    print(f"\nPinecone Settings:")
    print(f"API Key (first 10 chars): {settings.PINECONE_API_KEY[:10]}...")
    print(f"Environment: {settings.PINECONE_ENVIRONMENT}")
    print(f"Index Name: {settings.PINECONE_INDEX_NAME}")
    
    try:
        vector_store = get_vector_store()
        print("Successfully connected to Pinecone")
        
        # Test storing embeddings
        texts = ["Hello world", "Test message"]
        metadata = [{"source": "test"} for _ in texts]
        await vector_store.store_embeddings(texts, metadata, "test_namespace")
        print("Successfully stored embeddings")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

def test_connections():
    """Test both OpenAI and Pinecone connections"""
    settings = get_settings()
    
    # Test OpenAI
    print("\nTesting OpenAI connection...")
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello!"}]
    )
    print("OpenAI Test:", response.choices[0].message.content)

    # Test Pinecone
    print("\nTesting Pinecone connection...")
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    stats = index.describe_index_stats()
    print("Pinecone Test: Connected to index", stats)

if __name__ == "__main__":
    asyncio.run(test_vector_store())
    test_connections()
