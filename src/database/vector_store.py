# src/database/vector_store.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from src.utils import load_settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

config = load_settings()
vdb_config = config["vector_store"]

class RiskVectorDatabase:
    def __init__(self):
        import os
        # Read from environment variables if present (for cloud deployment), otherwise fallback to settings.yaml
        cloud_host = os.environ.get("QDRANT_HOST")
        cloud_api_key = os.environ.get("QDRANT_API_KEY")
        
        if cloud_host:
            self.client = QdrantClient(url=cloud_host, api_key=cloud_api_key)
        else:
            self.client = QdrantClient(host=vdb_config["host"], port=vdb_config["port"])
            
        self.collection_name = vdb_config["collection_name"]
        self.embeddings = GoogleGenerativeAIEmbeddings(model=vdb_config["embedding_model"])
        
    def initialize_collection(self, vector_size: int = 3072):
        """Creates the target namespace collection inside Qdrant if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            print(f"Collection '{self.collection_name}' successfully generated.")
        else:
            print(f"Collection '{self.collection_name}' already active.")

    def inject_document_chunk(self, doc_id: int, text_content: str, metadata: dict):
        """Embeds raw string content and registers it inside the vector store."""
        # 1. Generate dense text embeddings using Gemini's endpoint
        vector = self.embeddings.embed_query(text_content)
        
        # 2. Push point safely down into the storage system
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload={"text": text_content, **metadata} # Payload acts as metadata
                )
            ]
        )

    def query_semantic_context(self, query_text: str, limit: int = 3) -> list:
        """Performs a vector search to pull contextual data for agent prompts."""
        query_vector = self.embeddings.embed_query(query_text)
        
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        # Extract payload text strings matching search bounds
        return [hit.payload["text"] for hit in search_results if "text" in hit.payload]

if __name__ == "__main__":
    # Test script initialization pipeline
    vdb = RiskVectorDatabase()
    vdb.initialize_collection()
    
    # Insert trial data point
    vdb.inject_document_chunk(
        doc_id=101, 
        text_content="Taiwan's Hsinchu Science Park generates over 360 billion TWD in integrated circuit sales annually but faces escalating sea-level typhoon flood mechanics.",
        metadata={"source": "capstone_mock_report.pdf", "category": "climate_risk"}
    )
    
    # Query test context
    matches = vdb.query_semantic_context("Hsinchu semiconductor vulnerabilities")
    print("Found Matches:", matches)
