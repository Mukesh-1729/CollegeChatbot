# College Enquiry Chatbot using LLM and RAG Architecture

## 1. Abstract
The College Enquiry Chatbot using Large Language Models (LLMs) and Retrieval Augmented Generation (RAG) is designed to automate the process of answering student and parent queries related to academic programs, admissions, departments, placements, scholarships, and campus facilities. Traditional enquiry counters and manual response workflows are often slow, repetitive, and dependent on staff availability. This project addresses these limitations by integrating a modern conversational interface with a retrieval-driven intelligence layer.

The proposed system combines:
- A web scraping and preprocessing pipeline for institutional data collection.
- A semantic retrieval layer using embeddings and vector database indexing.
- An LLM-based response generation layer for natural language interaction.

The RAG architecture ensures that responses are generated using retrieved institutional context instead of relying only on the model's parametric memory. As a result, the chatbot delivers contextual, rapid, and scalable responses while reducing the operational burden on college administration teams.

## 2. Introduction
### 2.1 Background and Problem Statement
Many educational institutions still rely on manual enquiry mechanisms such as help desks, phone calls, or email-based support. These systems are often:
- Time-consuming for students and guardians.
- Repetitive for administrative staff.
- Limited by office hours and manpower.
- Inconsistent in response quality.

A college receives repeated questions on admissions, fee structure, departments, facilities, placement statistics, and contact information. Handling these manually creates delays and reduces efficiency.

### 2.2 Need for a Chatbot in Educational Institutions
A domain-specific chatbot can provide continuous and consistent support by:
- Offering instant responses to frequently asked queries.
- Reducing response time and user waiting periods.
- Supporting 24/7 access to institutional information.
- Improving student engagement and digital accessibility.

### 2.3 Proposed Solution Overview
This project implements an LLM-powered college enquiry assistant with a RAG pipeline. It first retrieves relevant information from a vector database built from official college web pages, then conditions the LLM prompt on this retrieved context to generate accurate answers.

## 3. Objectives
The main objectives of the project are:
- Automate answering of college-related queries from students, parents, and visitors.
- Provide accurate, contextual, and instant responses using RAG.
- Reduce human workload at enquiry desks and administrative offices.
- Maintain a scalable architecture that can be updated by re-running data ingestion.
- Deliver a user-friendly chat interface for improved accessibility.

## 4. System Architecture
### 4.1 High-Level Architecture
The solution follows a multi-layer architecture:
- User Interface Layer: Web-based chatbot interface for user interaction.
- Application Layer: Backend APIs for query handling and orchestration.
- Retrieval Layer: Embedding model plus vector similarity search.
- Generation Layer: LLM for final answer synthesis.

### 4.2 Data and Query Flow
1. User submits a question from the frontend.
2. Backend receives the question through API endpoint.
3. Question is transformed into an embedding vector.
4. Vector DB performs similarity search and returns top-k relevant chunks.
5. Retrieved context plus question is passed to the LLM.
6. LLM generates grounded response.
7. Response and source links are returned to the frontend.

### 4.3 Clean ASCII Architecture Diagram
```text
+-------------------+
|       User        |
| (Student/Parent)  |
+---------+---------+
          |
          v
+-------------------+
|  Frontend (Web)   |
| HTML/CSS/JS Chat  |
+---------+---------+
          |
          v
+-------------------+
| Backend API Layer |
| Node.js + FastAPI |
+---------+---------+
          |
          v
+-------------------------------+
| Retrieval Engine (RAG)        |
| - Query Embedding             |
| - Similarity Search (Top-k)   |
+---------+---------------------+
          |
          v
+-------------------------------+
| Vector Database               |
| FAISS / ChromaDB             |
| (Embedded text chunks)        |
+---------+---------------------+
          |
          v
+-------------------------------+
| LLM Inference Layer           |
| Gemini / OpenAI / Groq-Llama  |
+---------+---------------------+
          |
          v
+-------------------------------+
| Final Response + Sources      |
+-------------------------------+
```

## 5. Technologies Used
### 5.1 Frontend: HTML, CSS, JavaScript
- Purpose: Build responsive and interactive chat user interface.
- Reason for selection:
  - Lightweight and easy to deploy.
  - Full control over UI behavior and styling.
  - Native browser support without heavy frameworks.

### 5.2 Backend: Node.js and Express.js
- Purpose: Serve frontend, proxy API requests, and coordinate communication with Python services.
- Reason for selection:
  - Non-blocking I/O for efficient request handling.
  - Fast setup for REST-style communication.
  - Easy integration with static assets and middleware.

### 5.3 AI Model: LLM (Gemini / OpenAI)
- Purpose: Generate natural language answers from retrieved context.
- Reason for selection:
  - Strong language understanding and generation quality.
  - Ability to produce coherent, user-friendly responses.
  - API-based integration suitable for production chat systems.

Note: In this repository, the current implementation uses a Groq-hosted Llama model. The architecture remains compatible with Gemini or OpenAI with minimal API-layer changes.

### 5.4 Embeddings: Sentence Transformers
- Purpose: Convert text chunks and user queries into dense vectors.
- Reason for selection:
  - Strong semantic representation capability.
  - Efficient model variants for CPU-based deployment.
  - Well-suited for retrieval tasks in RAG systems.

### 5.5 Vector Database: FAISS / ChromaDB
- Purpose: Perform nearest-neighbor search over embedded knowledge chunks.
- Reason for selection:
  - Fast similarity retrieval for top-k relevant context.
  - Scalable indexing for large institutional documents.
  - Supports modular RAG experimentation.

### 5.6 Web Scraping: Python, BeautifulSoup
- Purpose: Extract data from the official college website.
- Reason for selection:
  - Robust HTML parsing and content extraction.
  - Python ecosystem support for data processing pipelines.
  - Easy automation for periodic data refresh.

## 6. Methodology
The working pipeline consists of the following stages:

1. Web Scraping of College Website
- Crawl seed URLs and discovered internal links.
- Extract page title, URL, and primary textual content.
- Save raw structured data in JSON format.

2. Data Cleaning and Preprocessing
- Remove noise, repeated symbols, and extra whitespace.
- Normalize extracted text while preserving useful entities.
- Retain source metadata (title, URL) for traceability.

3. Text Chunking
- Split long content into manageable overlapping chunks.
- Preserve sentence-level coherence where possible.
- Attach metadata to each chunk for source attribution.

4. Embedding Generation
- Use Sentence Transformers model to encode each chunk.
- Produce fixed-length numerical vectors.
- Normalize vectors for stable similarity comparison.

5. Storing Embeddings in Vector Database
- Build FAISS (or Chroma) index from vectors.
- Persist index and chunk metadata on disk.
- Prepare retrieval-ready knowledge base.

6. Query Embedding and Similarity Search
- Convert user query to embedding vector.
- Search vector DB for top-k semantically related chunks.
- Optionally combine keyword and vector retrieval (hybrid search).

7. Context Injection into LLM
- Construct prompt using retrieved chunks and source links.
- Add instruction constraints to reduce hallucination.
- Submit prompt to configured LLM API.

8. Final Response Generation
- LLM generates context-grounded answer.
- Backend returns answer and source references.
- Frontend displays response in conversational format.

## 7. Implementation Details
This section provides representative implementation snippets aligned with the architecture.

### 7.1 Web Scraping (Python + BeautifulSoup)
```python
import requests
from bs4 import BeautifulSoup

url = "https://bvrit.ac.in/about-bvrit/"
resp = requests.get(url, timeout=20)
soup = BeautifulSoup(resp.text, "lxml")

title = soup.title.get_text(strip=True) if soup.title else "Untitled"
text = " ".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))

page_data = {
    "url": url,
    "title": title,
    "content": text,
}
print(page_data["title"])
```

### 7.2 Embedding Generation (Sentence Transformers)
```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
chunks = ["Admission process details...", "Placement statistics..."]

embeddings = model.encode(chunks, batch_size=32, show_progress_bar=False)
embeddings = np.array(embeddings, dtype="float32")
```

### 7.3 Vector Search (FAISS)
```python
import faiss
import numpy as np

# embeddings: shape (N, D), dtype float32
D = embeddings.shape[1]
index = faiss.IndexFlatL2(D)
faiss.normalize_L2(embeddings)
index.add(embeddings)

query = model.encode(["What is the admission process?"])
query = np.array(query, dtype="float32")
faiss.normalize_L2(query)

distances, indices = index.search(query, k=5)
print(indices[0])
```

### 7.4 Backend API (Node.js + Express)
```javascript
const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");

const app = express();
app.use(express.json());

app.use(
  "/api",
  createProxyMiddleware({
    target: "http://127.0.0.1:5000",
    changeOrigin: true,
    pathRewrite: { "^/api": "" },
  })
);

app.listen(3000, () => console.log("Server running on 3000"));
```

### 7.5 LLM API Call (Gemini/OpenAI-Compatible Pattern)
```python
# Example pattern; replace with provider-specific client initialization

def build_prompt(question, context):
    return f"""
Use only the context below to answer the user question.

Context:
{context}

Question: {question}
"""

# Pseudocode for API call
# response = llm_client.generate(prompt=build_prompt(question, retrieved_context))
# answer = response.text
```

### 7.6 Frontend Chat UI (HTML + JavaScript)
```html
<div id="chatMessages"></div>
<textarea id="userInput" placeholder="Ask about admissions, fees, placements..."></textarea>
<button id="sendBtn">Send</button>
```

```javascript
async function sendMessage(question) {
  const res = await fetch("http://localhost:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: 5 }),
  });

  const data = await res.json();
  console.log("Answer:", data.answer);
  console.log("Sources:", data.sources || []);
}
```

## 8. Features
- Real-time query answering through a web-based conversational interface.
- No manually curated predefined Q/A dataset required.
- Retrieval-driven architecture that scales with newly scraped content.
- Source-aware responses with URL traceability.
- 24/7 availability for student support and information access.

## 9. Advantages
- Faster response time compared to manual enquiry workflows.
- Significant reduction in repetitive administrative effort.
- Improved consistency and accessibility of institutional information.
- Intelligent natural language responses powered by LLMs.
- Easy update cycle by re-running scraping and embedding pipeline.

## 10. Limitations
- Requires stable internet connectivity for API-based model access.
- Operational cost depends on LLM API pricing and usage volume.
- Retrieved content quality depends on website structure and freshness.
- Hallucination risk still exists if prompts are weak or retrieval is poor.
- Domain drift can occur if the source website changes significantly.

## 11. Future Enhancements
- Voice-enabled chatbot (speech-to-text and text-to-speech).
- Multilingual support for regional and international students.
- Mobile application integration (Android/iOS).
- Advanced RAG with rerankers and citation confidence scores.
- Fine-tuned or instruction-tuned domain LLM for higher factual precision.
- Admin dashboard for analytics, feedback, and continuous improvement.

## 12. Conclusion
The College Enquiry Chatbot using LLM and RAG Architecture demonstrates a practical and scalable approach to modernizing student support systems in educational institutions. By integrating automated data ingestion, semantic retrieval, and LLM-based response generation, the system offers fast, context-aware, and user-friendly enquiry handling.

This architecture reduces manual workload, improves information accessibility, and supports continuous updates as institutional data evolves. The project is suitable for academic mini-project implementation as well as real-world institutional deployment with incremental enhancements.

## 13. References
[1] OpenAI, "GPT-4 Technical Report," arXiv:2303.08774, 2023.

[2] H. Touvron et al., "Llama 2: Open Foundation and Fine-Tuned Chat Models," arXiv:2307.09288, 2023.

[3] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, and M. Wang, "Retrieval-Augmented Generation for Large Language Models: A Survey," arXiv:2312.10997, 2023.

[4] Meta AI, "Introducing Meta Llama 3: The most capable openly available LLM to date," 2024. [Online]. Available: https://ai.meta.com/blog/meta-llama-3/

[5] Google, "Gemini API Documentation," Google AI for Developers, 2025. [Online]. Available: https://ai.google.dev

[6] OpenAI, "OpenAI API Platform Documentation," 2025. [Online]. Available: https://platform.openai.com/docs

[7] H. Nori, Y. Zhang, R. Carignan, and E. Horvitz, "Can Generalist Foundation Models Outcompete Special-Purpose Tuning? Case Study in Medicine," arXiv:2311.16452, 2023.

[8] Meta AI Research, "FAISS: A library for efficient similarity search and clustering of dense vectors," documentation, 2024. [Online]. Available: https://github.com/facebookresearch/faiss

[9] UKPLab, "Sentence-Transformers Documentation," 2025. [Online]. Available: https://www.sbert.net

[10] Chroma, "Chroma Documentation," 2025. [Online]. Available: https://docs.trychroma.com

---

### IEEE-Style Notes for Final Report Integration
- Convert this markdown into IEEE double-column format using your preferred LaTeX or Word IEEE template.
- Replace placeholder implementation snippets with exact module references from your repository where required.
- Add experimental results section (accuracy, latency, user satisfaction) if needed by your conference track.
