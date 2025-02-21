from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .web_scraper import get_content


def initialize_client(collection_name: str):
    """
    Initializes and returns ChromaDB client, collection, and text splitter
    """
    client = chromadb.PersistentClient(path="./chroma_db")
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    return collection, text_splitter


def chunk_and_store(collection, text_splitter, texts: List[str], metadata: List[Dict[str, Any]] = None) -> None:
    """
    Chunks the input texts and stores them in the vector database

    Args:
        collection: ChromaDB collection
        text_splitter: Text splitter instance
        texts: List of texts to chunk and store
        metadata: Optional list of metadata dicts for each text
    """
    if metadata is None:
        metadata = [{} for _ in texts]
        
    all_chunks = []
    all_metadata = []
    all_ids = []
    
    for idx, (text, meta) in enumerate(zip(texts, metadata)):
        chunks = text_splitter.split_text(text)
        
        for chunk_idx, chunk in enumerate(chunks):
            chunk_id = f"chunk_{idx}_{chunk_idx}"
            all_chunks.append(chunk)
            all_metadata.append({**meta, "chunk_index": chunk_idx})
            all_ids.append(chunk_id)
    
    collection.add(
        documents=all_chunks,
        metadatas=all_metadata,
        ids=all_ids
    )


def store_content(url: str, collection_name: str):

    try:
        # Get website content
        content = get_content(url)

        # Initialize ChromaDB client and text splitter
        collection, text_splitter = initialize_client(collection_name)

        # Chunk and store content
        chunk_and_store(collection, text_splitter, content)
    
    except Exception as e:
        print(f"Error in crawler for {url}: {e}")


def retrieve_relevant(collection, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieves the most relevant chunks for a given query
    
    Args:
        collection: ChromaDB collection
        query: The query text to find relevant chunks for
        n_results: Number of results to return
        
    Returns:
        List of dictionaries containing the relevant chunks and their metadata
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    print(f"Retrived Results: {results}")
    
    retrieved_chunks = results["documents"][0]
    retrieved_chunks = [chunk for chunk in retrieved_chunks if chunk is not None]
    
    return retrieved_chunks