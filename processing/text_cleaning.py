"""
Data Processing Module
Cleans scraped text and splits into chunks for embedding generation.
"""

import os
import re
import json


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
INPUT_JSON = os.path.join(DATA_DIR, "scraped_pages.json")
OUTPUT_CHUNKS = os.path.join(DATA_DIR, "text_chunks.json")

# Chunk settings
CHUNK_SIZE = 1200      # characters per chunk (larger for detailed faculty pages)
CHUNK_OVERLAP = 200    # overlap between chunks


def clean_text(text):
    """Deep-clean the text content."""
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'&#\d+;', ' ', text)
    
    # Keep URLs and emails — they contain important contact/reference info
    # Only remove tracking/noise URLs if needed
    
    # Remove phone-style patterns that are just noise
    # (keep actual phone numbers)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove repeated punctuation
    text = re.sub(r'([.\-_=])\1{3,}', '', text)
    
    # Strip
    text = text.strip()
    
    return text


def split_into_chunks(text, source_url="", title="", chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Split text into overlapping chunks.
    Each chunk includes metadata about its source.
    """
    if not text or len(text) < 50:
        return []
    
    chunks = []
    
    # Split by sentences first for better boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "source": source_url,
                    "title": title,
                    "chunk_id": len(chunks)
                })
            
            # Start new chunk with overlap (include last part of previous chunk)
            if overlap > 0 and current_chunk:
                overlap_text = current_chunk[-overlap:]
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk = sentence
    
    # Don't forget the last chunk
    if current_chunk and len(current_chunk.strip()) > 30:
        chunks.append({
            "text": current_chunk.strip(),
            "source": source_url,
            "title": title,
            "chunk_id": len(chunks)
        })
    
    return chunks


def process_scraped_data():
    """Main processing pipeline."""
    print("=" * 60)
    print("  Data Processing Module")
    print("=" * 60)
    
    # Load scraped data
    if not os.path.exists(INPUT_JSON):
        print(f"\n[ERROR] Input file not found: {INPUT_JSON}")
        print("Please run the scraper first: python scraper/scrape_college_data.py")
        return []
    
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        pages = json.load(f)
    
    print(f"\n[1] Loaded {len(pages)} scraped pages")
    
    # Process each page
    all_chunks = []
    
    # Department slug-to-name mapping for URL context
    DEPT_NAMES = {
        'aids': 'Artificial Intelligence and Data Science (AI & DS)',
        'cse': 'Computer Science and Engineering (CSE)',
        'cse-ai-ml': 'Computer Science and Engineering - Artificial Intelligence and Machine Learning (CSE-AI&ML)',
        'cse-ds': 'Computer Science and Engineering - Data Science (CSE-DS)',
        'csbs': 'Computer Science and Business Systems (CSBS)',
        'it': 'Information Technology (IT)',
        'ece': 'Electronics and Communication Engineering (ECE)',
        'eee': 'Electrical and Electronics Engineering (EEE)',
        'mech': 'Mechanical Engineering',
        'civil': 'Civil Engineering',
        'che': 'Chemical Engineering',
        'bme': 'Biomedical Engineering (BME)',
        'phe': 'Pharmaceutical Engineering',
        'bs-h': 'Basic Sciences and Humanities (BS&H)',
        'mba': 'Master of Business Administration (MBA)',
        'cse-pg': 'CSE Post Graduate',
    }

    for page in pages:
        cleaned_content = clean_text(page.get("content", ""))
        
        if len(cleaned_content) < 50:
            continue
        
        # Include title context in the content
        title = page.get("title", "")
        if title:
            cleaned_content = f"{title}. {cleaned_content}"
        
        # Add department context from URL path
        url = page.get("url", "")
        from urllib.parse import urlparse
        path_parts = urlparse(url).path.strip('/').split('/')
        if path_parts:
            dept_slug = path_parts[0]
            dept_name = DEPT_NAMES.get(dept_slug)
            if dept_name:
                page_type = path_parts[1] if len(path_parts) > 1 else 'department'
                cleaned_content = f"Department: {dept_name}. Page: {page_type}. {cleaned_content}"
        
        chunks = split_into_chunks(
            cleaned_content,
            source_url=page.get("url", ""),
            title=title
        )
        
        all_chunks.extend(chunks)
    
    # Inject a synthetic "all departments" summary chunk so the chatbot
    # can always answer "what departments does BVRIT have?"
    dept_summary = (
        "Departments and Branches at BVRIT. "
        "BVRIT (B V Raju Institute of Technology) offers the following undergraduate and postgraduate departments and branches: "
        "1. Computer Science and Engineering (CSE) "
        "2. CSE - Artificial Intelligence and Machine Learning (CSE-AI&ML) "
        "3. CSE - Data Science (CSE-DS) "
        "4. Artificial Intelligence and Data Science (AI&DS / AIDS) "
        "5. Computer Science and Business Systems (CSBS) "
        "6. Information Technology (IT) "
        "7. Electronics and Communication Engineering (ECE) "
        "8. Electrical and Electronics Engineering (EEE) "
        "9. Mechanical Engineering (Mech) "
        "10. Civil Engineering "
        "11. Chemical Engineering "
        "12. Biomedical Engineering (BME) "
        "13. Pharmaceutical Engineering (PHE) "
        "14. Basic Sciences and Humanities (BS&H) "
        "15. Master of Business Administration (MBA) "
        "16. CSE Post Graduate (CSE-PG). "
        "CSE, IT, ECE, EEE, Chemical, Mechanical, and Civil Engineering branches are accredited by NBA."
    )
    all_chunks.append({
        "text": dept_summary,
        "source": "https://bvrit.ac.in/about-bvrit/",
        "title": "Departments and Branches at BVRIT",
        "chunk_id": 0
    })

    print(f"[2] Generated {len(all_chunks)} text chunks")
    print(f"    Average chunk size: {sum(len(c['text']) for c in all_chunks) // max(len(all_chunks), 1)} chars")
    
    # Assign global IDs
    for i, chunk in enumerate(all_chunks):
        chunk["global_id"] = i
    
    # Save chunks
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_CHUNKS, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"[3] Saved chunks to: {OUTPUT_CHUNKS}")
    print(f"\n{'='*60}")
    
    return all_chunks


if __name__ == "__main__":
    process_scraped_data()
