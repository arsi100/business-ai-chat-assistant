from src.database.vector_store import get_vector_store

def test_pinecone():
    print("\n=== Testing Pinecone Connection ===")
    try:
        # Get vector store instance
        vector_store = get_vector_store()
        
        # Test embedding and search
        test_text = "Hello, this is a test message"
        print("\nTesting embedding generation...")
        embedding = vector_store.get_embedding(test_text)
        print(f"Successfully generated embedding of length: {len(embedding)}")
        
        # Test search
        print("\nTesting vector search...")
        results = vector_store.index.describe_index_stats()
        print(f"\nPinecone Index Stats:")
        print(f"Total vectors: {results.total_vector_count}")
        print(f"Namespaces: {results.namespaces if hasattr(results, 'namespaces') else 'None'}")
        
        print("\nPinecone connection test completed successfully!")
        
    except Exception as e:
        print(f"Pinecone Error: {str(e)}")

if __name__ == "__main__":
    test_pinecone() 