# ingest.py
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# --- Configuration ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen:0.5b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")  # Use env var directly
VECTOR_DB_PATH = "faiss_index"
MANUAL_PATH = "data/Washing Machine Service Manual.pdf"

def ingest_manual():
    print("--- Starting Document Ingestion ---")
    print(f"OLLAMA_HOST for ingestion: {OLLAMA_HOST}")
    print(f"OLLAMA_MODEL for ingestion: {OLLAMA_MODEL}")

    if not os.path.exists(MANUAL_PATH):
        print(f"Error: Service manual not found at {MANUAL_PATH}")
        print("Please place your 'Washing Machine Service Manual.pdf' in the 'data' folder.")
        return

    print("1. Loading document...")
    try:
        loader = PyPDFLoader(MANUAL_PATH)
        documents = loader.load()
        print(f"Loaded {len(documents)} pages.")
    except Exception as e:
        print(f"Error loading PDF document: {e}")
        return

    print("2. Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} text chunks.")

    print(f"3. Initializing Ollama embeddings with model: {OLLAMA_MODEL}...")
    try:
        embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_HOST)
        # Test embeddings to ensure Ollama is accessible
        _ = embeddings.embed_query("test query")
        print("Ollama embeddings initialized successfully.")
    except Exception as e:
        print(f"Error initializing Ollama embeddings: {e}")
        print(f"OLLAMA_HOST currently set to: {OLLAMA_HOST}")
        print("Please ensure Ollama is running and the specified model is available.")
        print(f"You can pull the model using: ollama pull {OLLAMA_MODEL}")
        return

    print(f"4. Creating FAISS vector store and saving to {VECTOR_DB_PATH}...")
    try:
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(VECTOR_DB_PATH)
        print(f"Vector store created and saved successfully to {VECTOR_DB_PATH}/")
    except Exception as e:
        print(f"Error creating or saving FAISS vector store: {e}")
        return

    print("--- Ingestion Complete ---")

if __name__ == "__main__":
    # Ensure Ollama model is pulled (unchanged)
    print(f"Attempting to pull Ollama model '{OLLAMA_MODEL}' if not already present...")
    try:
        os.system(f"ollama pull {OLLAMA_MODEL}")
        print("Ollama model pull command executed. Check console for status.")
    except Exception as e:
        print(f"Could not execute 'ollama pull' command: {e}")
        print("Please ensure Ollama is installed and running, and the 'ollama' command is in your PATH.")

    ingest_manual()
