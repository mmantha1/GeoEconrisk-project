# src/database/ingest_data.py
import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.database.vector_store import RiskVectorDatabase

def run_data_ingestion_pipeline():
    """
    Scans the data/raw folder for text documents, splits them semantically,
    and bulk injects them directly into the Qdrant database.
    """
    # 1. Initialize our custom vector database connector handle
    db = RiskVectorDatabase()
    db.initialize_collection()
    
    # 2. Configure the text splitter framework
    # Chunks are set to 1000 characters with a 150-character overlap 
    # to ensure sentences aren't cut in half across chunks.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    
    raw_data_dir = "data/raw"
    search_path = os.path.join(raw_data_dir, "*.txt")
    target_files = glob.glob(search_path)
    
    if not target_files:
        print(f"⚠️ No training documents (.txt) found in directory context: '{raw_data_dir}/'")
        print("Please place text documents inside 'data/raw/' to continue seed upload sequence.")
        return

    print(f"📂 Found {len(target_files)} document profiles ready for vectorization mapping...")
    
    global_chunk_id = 1
    
    for file_path in target_files:
        filename = os.path.basename(file_path)
        print(f"📖 Reading structural file logs: {filename}...")
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                raw_text_content = file.read()
                
            # 3. Partition raw file bodies into strategic document vectors
            document_chunks = text_splitter.split_text(raw_text_content)
            print(f"   ↳ Generated {len(document_chunks)} discrete text nodes.")
            
            # 4. Inject each chunk along with tracking metadata parameters
            for index, chunk in enumerate(document_chunks):
                metadata = {
                    "source_file": filename,
                    "chunk_index": index
                }
                
                db.inject_document_chunk(
                    doc_id=global_chunk_id,
                    text_content=chunk,
                    metadata=metadata
                )
                global_chunk_id += 1
                
            print(f"✅ Successfully synchronized file contents: {filename}")
            
        except Exception as e:
            print(f"❌ Aborted upload handling sequence for file [{filename}]: {str(e)}")

    print(f"\n🚀 System Sync Complete! Injected a total of {global_chunk_id - 1} records into Qdrant.")

if __name__ == "__main__":
    run_data_ingestion_pipeline()
