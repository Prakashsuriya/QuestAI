import os
import json
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

class VectorStore:
    """Vector database for document embeddings using ChromaDB."""
    
    def __init__(self, collection_name: str = "documents"):
        self.persist_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'chroma_db')
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Use default embedding function (all-MiniLM-L6-v2)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
    
    def add_document(self, text: str, metadata: Dict[str, Any]) -> str:
        """Add a document to the vector store."""
        doc_id = f"{metadata['document_id']}_{metadata['chunk_id']}"
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def search(self, query: str, user_id: int, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"user_id": user_id} if user_id else None
        )
        
        documents = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0.0
                })
        
        return documents
    
    def delete_document(self, doc_id: str):
        """Delete a document from the vector store."""
        try:
            self.collection.delete(ids=[doc_id])
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            embedding_function=self.embedding_function
        )
