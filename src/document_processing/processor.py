from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import (
    TextLoader,
    PDFLoader,
    CSVLoader,
    JSONLoader
)
import json
from pathlib import Path
from ..database.vector_store import get_vector_store

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = get_vector_store()
    
    def _extract_text_from_json(self, json_data: Dict) -> List[str]:
        """Recursively extract all string values from JSON"""
        texts = []
        
        def extract_strings(obj):
            if isinstance(obj, str):
                texts.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_strings(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_strings(item)
        
        extract_strings(json_data)
        return texts
        
    async def process_document(self, file_path: str, client_id: str, json_fields: Optional[List[str]] = None) -> None:
        """
        Process a document and store it in the vector database
        
        Args:
            file_path: Path to the document
            client_id: Client identifier
            json_fields: Optional list of specific JSON fields to process (e.g., ['description', 'title'])
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        try:
            if extension == '.txt':
                loader = TextLoader(file_path)
                documents = loader.load()
            elif extension == '.pdf':
                loader = PDFLoader(file_path)
                documents = loader.load()
            elif extension == '.csv':
                loader = CSVLoader(file_path)
                documents = loader.load()
            elif extension == '.json':
                # Handle JSON files more flexibly
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                
                if json_fields:
                    # Extract only specified fields
                    texts = []
                    for item in (json_data if isinstance(json_data, list) else [json_data]):
                        text_parts = []
                        for field in json_fields:
                            if field in item:
                                text_parts.append(f"{field}: {item[field]}")
                        if text_parts:
                            texts.append(" ".join(text_parts))
                else:
                    # Extract all text content
                    texts = self._extract_text_from_json(json_data)
                
                # Convert to document format
                documents = [
                    Document(
                        page_content=text,
                        metadata={
                            "source": file_path,
                            "file_type": "json"
                        }
                    ) for text in texts if text.strip()
                ]
            else:
                raise ValueError(f"Unsupported file type: {extension}. Supported types: .txt, .pdf, .csv, .json")
            
            # Split documents
            texts = self.text_splitter.split_documents(documents)
            
            # Prepare for storage
            text_chunks = [doc.page_content for doc in texts]
            metadata = [
                {
                    "source": file_path,
                    "client_id": client_id,
                    "file_type": extension,
                    **doc.metadata
                } for doc in texts
            ]
            
            # Store in vector database
            await self.vector_store.store_embeddings(
                texts=text_chunks,
                metadata=metadata,
                namespace=client_id
            )
            
        except Exception as e:
            raise Exception(f"Error processing document {file_path}: {str(e)}")

    async def process_raw_text(self, text: str, client_id: str, source_name: str = "direct_input") -> None:
        """Process raw text input"""
        texts = self.text_splitter.split_text(text)
        
        metadata = [
            {
                "source": source_name,
                "client_id": client_id,
                "file_type": "raw_text",
            } for _ in texts
        ]
        
        await self.vector_store.store_embeddings(
            texts=texts,
            metadata=metadata,
            namespace=client_id
        )

# Singleton instance
processor: DocumentProcessor = None

def get_processor() -> DocumentProcessor:
    """Get or create document processor instance"""
    global processor
    if processor is None:
        processor = DocumentProcessor()
    return processor 