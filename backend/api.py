"""
Python FastAPI Backend
Handles query processing, vector search, and LLM response generation.
Run with: uvicorn api:app --host 0.0.0.0 --port 5000 --reload
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from embeddings.generate_embeddings import search_similar, SentenceTransformer, MODEL_NAME
from llm.query_llm import query_gemini
import faiss
import pickle

app = FastAPI(title="College Chatbot API", version="1.0.0")

# CORS — allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for loaded models
embedding_model = None
faiss_index = None
chunks_metadata = None

VECTOR_DB_DIR = os.path.join(PROJECT_ROOT, "vector_db")
FAISS_INDEX_PATH = os.path.join(VECTOR_DB_DIR, "faiss_index.bin")
CHUNKS_METADATA_PATH = os.path.join(VECTOR_DB_DIR, "chunks_metadata.pkl")


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 10


class QueryResponse(BaseModel):
    answer: str
    sources: list
    status: str


@app.on_event("startup")
async def load_models():
    """Load embedding model and FAISS index on startup."""
    global embedding_model, faiss_index, chunks_metadata
    
    print("Loading embedding model...")
    embedding_model = SentenceTransformer(MODEL_NAME)
    print("Embedding model loaded.")
    
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(CHUNKS_METADATA_PATH):
        print("Loading FAISS index...")
        faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        
        with open(CHUNKS_METADATA_PATH, 'rb') as f:
            chunks_metadata = pickle.load(f)
        
        print(f"FAISS index loaded with {faiss_index.ntotal} vectors.")
    else:
        print("WARNING: Vector database not found. Please run the pipeline first.")
        print("  1. python scraper/scrape_college_data.py")
        print("  2. python processing/text_cleaning.py")
        print("  3. python embeddings/generate_embeddings.py")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "College Chatbot API",
        "vector_db_loaded": faiss_index is not None
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "embedding_model": embedding_model is not None,
        "faiss_index": faiss_index is not None,
        "total_vectors": faiss_index.ntotal if faiss_index else 0,
        "total_chunks": len(chunks_metadata) if chunks_metadata else 0
    }


@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """Main chat endpoint — process user question and return answer."""
    question = request.question.strip()
    
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if faiss_index is None or chunks_metadata is None:
        raise HTTPException(
            status_code=503, 
            detail="Vector database not loaded. Please run the data pipeline first."
        )
    
    try:
        # Step 1: Retrieve relevant chunks
        results = search_similar(
            query=question,
            model=embedding_model,
            index=faiss_index,
            chunks=chunks_metadata,
            top_k=request.top_k
        )
        
        if not results:
            return QueryResponse(
                answer="I couldn't find relevant information to answer your question. Please try rephrasing or visit https://bvrit.ac.in for more details.",
                sources=[],
                status="no_results"
            )
        
        # Step 2: Generate LLM response
        answer = query_gemini(results, question)
        
        # Step 3: Collect sources
        sources = list(set([r["source"] for r in results if r.get("source")]))
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            status="success"
        )
        
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search_only(request: QueryRequest):
    """Search endpoint — returns relevant chunks without LLM processing."""
    question = request.question.strip()
    
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if faiss_index is None:
        raise HTTPException(status_code=503, detail="Vector database not loaded.")
    
    results = search_similar(
        query=question,
        model=embedding_model,
        index=faiss_index,
        chunks=chunks_metadata,
        top_k=request.top_k
    )
    
    return {"results": results}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=5000, reload=True)
