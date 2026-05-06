"""
Full Pipeline Runner
Runs all steps: Scrape → Process → Embed → Build Vector DB

Usage:
    python run_pipeline.py
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


def run_full_pipeline():
    """Execute the complete data pipeline."""
    start_time = time.time()
    
    print("\n" + "=" * 60)
    print("  BVRIT College Chatbot — Full Data Pipeline")
    print("=" * 60)
    
    # Step 1: Scrape
    print("\n" + "─" * 60)
    print("  STEP 1/3: Web Scraping")
    print("─" * 60)
    from scraper.scrape_college_data import scrape_college
    pages = scrape_college()
    
    if not pages:
        print("\n[ERROR] No pages scraped. Aborting pipeline.")
        return
    
    # Step 2: Process
    print("\n" + "─" * 60)
    print("  STEP 2/3: Data Processing")
    print("─" * 60)
    from processing.text_cleaning import process_scraped_data
    chunks = process_scraped_data()
    
    if not chunks:
        print("\n[ERROR] No chunks generated. Aborting pipeline.")
        return
    
    # Step 3: Build Vector Database
    print("\n" + "─" * 60)
    print("  STEP 3/3: Embedding Generation & Vector DB")
    print("─" * 60)
    from embeddings.generate_embeddings import build_vector_db
    build_vector_db()
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"  PIPELINE COMPLETE — took {elapsed:.1f} seconds")
    print("=" * 60)
    print("\n  Next steps:")
    print("  1. Set your Gemini API key in .env file")
    print("  2. Start Python API:  cd backend && python api.py")
    print("  3. Start Node server: npm start")
    print("  4. Open: http://localhost:3000")
    print()


if __name__ == "__main__":
    run_full_pipeline()
