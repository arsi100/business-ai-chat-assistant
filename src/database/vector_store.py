from typing import List, Dict, Any
from pinecone import Pinecone
from openai import OpenAI
from ..config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

class VectorStore:
    def __init__(self):
        """Initialize Pinecone client"""
        self.pc = Pinecone(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    
    async def store_embeddings(
        self,
        texts: List[str],
        metadata: List[Dict[str, Any]],
        namespace: str
    ):
        """Store text embeddings in Pinecone"""
        vectors = []
        
        for i, text in enumerate(texts):
            embedding = self.get_embedding(text)
            vectors.append({
                'id': f"{namespace}-{i}",
                'values': embedding,
                'metadata': {
                    'text': text,
                    **metadata[i]
                }
            })
        
        # Batch upsert to Pinecone
        self.index.upsert(
            vectors=vectors,
            namespace=namespace
        )
    
    async def search(
        self,
        query: str,
        namespace: str,
        top_k: int = 5
    ) -> List[Dict]:
        """Search for similar texts in the vector store"""
        query_embedding = self.get_embedding(query)
        
        results = self.index.query(
            vector=query_embedding,
            namespace=namespace,
            top_k=top_k,
            include_metadata=True
        )
        
        return [
            {
                'text': match['metadata']['text'],
                'score': match['score'],
                'metadata': match['metadata']
            }
            for match in results['matches']
        ]

# Singleton instance
vector_store: VectorStore = None

def get_vector_store() -> VectorStore:
    """Get or create vector store instance"""
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store 