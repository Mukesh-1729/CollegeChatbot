"""
Embedding Generation Module
Converts text chunks into vector embeddings using Sentence Transformers
and stores them in a FAISS vector index.
"""

import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
VECTOR_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_db")
INPUT_CHUNKS = os.path.join(DATA_DIR, "text_chunks.json")
FAISS_INDEX_PATH = os.path.join(VECTOR_DB_DIR, "faiss_index.bin")
CHUNKS_METADATA_PATH = os.path.join(VECTOR_DB_DIR, "chunks_metadata.pkl")

# Embedding model — lightweight and effective
MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks():
    """Load text chunks from JSON."""
    if not os.path.exists(INPUT_CHUNKS):
        print(f"[ERROR] Chunks file not found: {INPUT_CHUNKS}")
        print("Please run processing first: python processing/text_cleaning.py")
        return []
    
    with open(INPUT_CHUNKS, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_embeddings(chunks, model):
    """Generate embeddings for all text chunks."""
    texts = [chunk["text"] for chunk in chunks]
    print(f"  Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    return np.array(embeddings, dtype='float32')


def build_faiss_index(embeddings):
    """Build a FAISS index from embeddings."""
    dimension = embeddings.shape[1]
    
    # Use L2 (Euclidean) distance index
    index = faiss.IndexFlatL2(dimension)
    
    # Normalize for cosine similarity behavior
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    
    return index


def save_index(index, chunks):
    """Save FAISS index and chunks metadata to disk."""
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    
    # Save FAISS index
    faiss.write_index(index, FAISS_INDEX_PATH)
    
    # Save chunks metadata
    with open(CHUNKS_METADATA_PATH, 'wb') as f:
        pickle.dump(chunks, f)
    
    print(f"  FAISS index saved to: {FAISS_INDEX_PATH}")
    print(f"  Metadata saved to: {CHUNKS_METADATA_PATH}")


# Topic-based URL patterns — boost chunks whose source URL matches a topic.
# Each entry: (query_phrase, url_substring, bonus_score)
_TOPIC_URL_BOOST = [
    # Department listing queries — boost about page AND each department home page
    ('departments', '/about-bvrit/', 10),
    ('branches', '/about-bvrit/', 10),
    ('all departments', '/about-bvrit/', 12),
    ('list of departments', '/about-bvrit/', 12),
    ('how many departments', '/about-bvrit/', 12),
    # Also slightly boost individual department home pages for "departments" queries
    ('departments', '/cse/', 3),
    ('departments', '/ece/', 3),
    ('departments', '/eee/', 3),
    ('departments', '/mech/', 3),
    ('departments', '/it/', 3),
    ('departments', '/csbs/', 3),
    ('departments', '/cse-ai-ml/', 3),
    ('departments', '/cse-ds/', 3),
    ('departments', '/aids/', 3),
    ('departments', '/bme/', 3),
    ('departments', '/phe/', 3),
    ('departments', '/mba/', 3),
    ('departments', '/che/', 3),
    # Placement queries — boost department-specific placement pages
    ('placement', '/department-placements/', 10),
    ('placement', '/placements/', 8),
    ('placement', '/placement-statistics/', 10),
    ('placement', '/placement-readiness/', 8),
    ('placement', '/interns-placements/', 8),
    ('placement', '/about-placement-cell/', 8),
    ('placement', '/placements-team/', 6),
    ('placements', '/department-placements/', 10),
    ('placements', '/placements/', 8),
    ('placements', '/placement-statistics/', 10),
    ('placements', '/placement-readiness/', 8),
    ('placements', '/interns-placements/', 8),
    ('placed', '/department-placements/', 8),
    ('placed', '/placements/', 6),
    ('package', '/department-placements/', 8),
    ('package', '/placement-statistics/', 8),
    ('salary', '/department-placements/', 6),
    ('recruit', '/department-placements/', 6),
    ('recruit', '/placements/', 6),
    ('companies', '/department-placements/', 6),
    ('companies', '/placements/', 6),
]

# Department URL slug detection — maps query phrases to URL path segments.
# Sorted by specificity (longer phrases checked first) to avoid partial matches.
_DEPT_URL_MAP = [
    # Most specific / longest first
    ('artificial intelligence and data science', '/aids/'),
    ('artificial intelligence and machine learning', '/cse-ai-ml/'),
    ('computer science and business systems', '/csbs/'),
    ('computer science business systems', '/csbs/'),
    ('information technology', '/it/'),
    ('business administration', '/mba/'),
    ('biomedical engineering', '/bme/'),
    ('mechanical engineering', '/mech/'),
    ('cse data science', '/cse-ds/'),
    ('ai and data science', '/aids/'),
    ('ai data science', '/aids/'),
    ('cse ai ml', '/cse-ai-ml/'),
    ('ai and ml', '/cse-ai-ml/'),
    ('ai & ml', '/cse-ai-ml/'),
    ('ai&ml', '/cse-ai-ml/'),
    ('ai&ds', '/aids/'),
    ('ai & ds', '/aids/'),
    ('cse-ai-ml', '/cse-ai-ml/'),
    ('cse-ds', '/cse-ds/'),
    ('cse ds', '/cse-ds/'),
    ('ai ml', '/cse-ai-ml/'),
    ('ai ds', '/aids/'),
    ('csbs', '/csbs/'),
    ('aids', '/aids/'),
    ('mech', '/mech/'),
    ('bme', '/bme/'),
    ('phe', '/phe/'),
    ('mba', '/mba/'),
    ('ece', '/ece/'),
    ('eee', '/eee/'),
    ('it department', '/it/'),
    ('it dept', '/it/'),
    # 'cse' last — it's a prefix of cse-ds and cse-ai-ml
    ('cse', '/cse/'),
]

# Department synonyms for expanding keyword queries.
# IMPORTANT: No cross-contamination between CSE-DS / AIDS / CSE-AI-ML.
_DEPT_SYNONYMS = {
    # AIDS (Artificial Intelligence and Data Science) — URL: /aids/
    'aids': ['artificial intelligence and data science', 'ai&ds', 'ai & ds'],
    'ai&ds': ['aids', 'artificial intelligence and data science'],
    'ai & ds': ['aids', 'artificial intelligence and data science'],
    'ai ds': ['aids', 'artificial intelligence and data science'],
    'ai and data science': ['aids', 'ai&ds'],
    # CSE-DS (CSE – Data Science) — URL: /cse-ds/
    'cse-ds': ['cse data science', 'computer science data science'],
    'cse ds': ['cse-ds', 'cse data science'],
    'cse data science': ['cse-ds'],
    # CSE-AI-ML (CSE – AI & ML) — URL: /cse-ai-ml/
    'cse-ai-ml': ['artificial intelligence and machine learning', 'cse ai ml'],
    'ai&ml': ['cse-ai-ml', 'artificial intelligence and machine learning'],
    'ai & ml': ['cse-ai-ml', 'artificial intelligence and machine learning'],
    'ai and ml': ['cse-ai-ml', 'artificial intelligence and machine learning'],
    'ai ml': ['cse-ai-ml', 'artificial intelligence and machine learning'],
    # CSBS
    'csbs': ['computer science and business systems'],
    # CSE (plain)
    'cse': ['computer science and engineering'],
    'computer science': ['cse'],
    # ECE
    'ece': ['electronics and communication', 'electronics'],
    'electronics': ['ece'],
    # EEE
    'eee': ['electrical and electronics', 'electrical'],
    'electrical': ['eee'],
    # Mechanical
    'mech': ['mechanical engineering', 'mechanical'],
    'mechanical': ['mech'],
    # IT
    'information technology': ['it department'],
    # BME
    'bme': ['biomedical engineering', 'biomedical'],
    'biomedical': ['bme'],
    # PHE
    'phe': ['pharmaceutical engineering', 'pharmaceutical'],
    'pharmaceutical': ['phe'],
    # MBA
    'mba': ['management', 'business administration'],
}


def _keyword_search(query, chunks, top_k=10):
    """
    Keyword-based search — finds chunks containing query terms.
    Uses URL slug detection + synonym expansion for department queries.
    """
    import re as _re
    query_lower = query.lower()
    # Allow 2-char words so "ai", "ml", "ds" are captured
    stop_words = {
        'the', 'what', 'who', 'how', 'tell', 'me', 'about', 'does', 'can',
        'are', 'was', 'for', 'and', 'with', 'is', 'in', 'of', 'to', 'at',
        'by', 'on', 'an', 'or', 'do', 'be', 'has', 'had', 'its', 'it',
        'my', 'we', 'so', 'if', 'no', 'up', 'he', 'she', 'us',
    }
    words = [w for w in _re.findall(r'\b[a-zA-Z]{2,}\b', query_lower) if w not in stop_words]

    # Detect target department URL slug (most specific/longest match first)
    target_slug = None
    for phrase, slug in _DEPT_URL_MAP:
        if phrase in query_lower:
            target_slug = slug
            break

    # Expand query with department synonyms
    expanded_phrases = []
    for key, synonyms in _DEPT_SYNONYMS.items():
        if key in query_lower:
            expanded_phrases.extend(synonyms)

    scored = []
    for i, chunk in enumerate(chunks):
        text_lower = chunk["text"].lower()
        title_lower = chunk.get("title", "").lower()
        source_lower = chunk.get("source", "").lower()
        combined = text_lower + " " + title_lower + " " + source_lower
        # Count how many query words appear in the chunk
        word_hits = sum(1 for w in words if w in combined)
        # Bonus for exact phrase match
        phrase_hit = 1 if query_lower in combined else 0
        # Bonus for expanded department synonym matches
        synonym_hits = sum(1 for phrase in expanded_phrases if phrase in combined)
        # BIG bonus when chunk belongs to the detected department URL
        url_bonus = 10 if (target_slug and target_slug in source_lower) else 0
        # Topic-based URL boosting (departments listing, placements, etc.)
        topic_bonus = 0
        for tphrase, turl, tbonus in _TOPIC_URL_BOOST:
            if tphrase in query_lower and turl in source_lower:
                topic_bonus = max(topic_bonus, tbonus)
        score = word_hits + phrase_hit * 3 + synonym_hits * 2 + url_bonus + topic_bonus
        if score > 0:
            scored.append((score, i))

    scored.sort(key=lambda x: -x[0])
    results = []
    for score, idx in scored[:top_k]:
        results.append({
            "text": chunks[idx]["text"],
            "source": chunks[idx].get("source", ""),
            "title": chunks[idx].get("title", ""),
            "score": float(score),
            "_keyword": True
        })
    return results


def search_similar(query, model=None, index=None, chunks=None, top_k=5):
    """
    Hybrid search: combines FAISS vector search with keyword search.
    Strong keyword hits (URL match / high score) prioritized, then vector
    results, then weaker keyword hits.
    """
    if model is None:
        model = SentenceTransformer(MODEL_NAME)
    
    if index is None:
        index = faiss.read_index(FAISS_INDEX_PATH)
    
    if chunks is None:
        with open(CHUNKS_METADATA_PATH, 'rb') as f:
            chunks = pickle.load(f)
    
    # 1) Keyword search — catches names, department slugs, specific terms
    keyword_results = _keyword_search(query, chunks, top_k=top_k * 2)
    
    # 2) Vector search — catches semantic meaning
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding, dtype='float32')
    faiss.normalize_L2(query_embedding)
    
    fetch_k = min(top_k * 4, index.ntotal)
    distances, indices = index.search(query_embedding, fetch_k)
    
    vector_results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(chunks):
            vector_results.append({
                "text": chunks[idx]["text"],
                "source": chunks[idx].get("source", ""),
                "title": chunks[idx].get("title", ""),
                "score": float(distances[0][i])
            })
    
    # 3) Merge: strong keyword hits first, then vector, then weak keyword
    seen_texts = set()
    merged = []
    
    # Strong keyword results (score >= 3 means multiple keyword hits or URL match)
    for r in keyword_results:
        if r["score"] >= 3:
            key = r["text"][:100]
            if key not in seen_texts:
                seen_texts.add(key)
                merged.append(r)
    
    # Vector results fill remaining slots
    for r in vector_results:
        key = r["text"][:100]
        if key not in seen_texts:
            seen_texts.add(key)
            merged.append(r)
    
    # Weak keyword results last
    for r in keyword_results:
        key = r["text"][:100]
        if key not in seen_texts:
            seen_texts.add(key)
            merged.append(r)
    
    return merged[:top_k]


def build_vector_db():
    """Main pipeline to build the vector database."""
    print("=" * 60)
    print("  Embedding Generation & Vector DB Builder")
    print("=" * 60)
    
    # Load chunks
    print("\n[1] Loading text chunks...")
    chunks = load_chunks()
    if not chunks:
        return
    print(f"    Loaded {len(chunks)} chunks")
    
    # Load embedding model
    print(f"\n[2] Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print("    Model loaded successfully")
    
    # Generate embeddings
    print(f"\n[3] Generating embeddings...")
    embeddings = generate_embeddings(chunks, model)
    print(f"    Embeddings shape: {embeddings.shape}")
    
    # Build FAISS index
    print(f"\n[4] Building FAISS index...")
    index = build_faiss_index(embeddings)
    print(f"    Index built with {index.ntotal} vectors")
    
    # Save
    print(f"\n[5] Saving index and metadata...")
    save_index(index, chunks)
    
    # Test search
    print(f"\n[6] Testing search...")
    test_query = "What is the admission process?"
    results = search_similar(test_query, model, index, chunks, top_k=3)
    print(f"    Query: '{test_query}'")
    for i, r in enumerate(results):
        print(f"    Result {i+1} (score: {r['score']:.4f}): {r['text'][:100]}...")
    
    print(f"\n{'='*60}")
    print("  Vector database built successfully!")
    print(f"{'='*60}")


if __name__ == "__main__":
    build_vector_db()
