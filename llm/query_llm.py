"""
LLM Query Module
Uses Groq API (Llama 3.3 70B) to generate responses based on retrieved context.
Free tier: 30 req/min, 14,400 req/day — extremely fast inference.
"""

import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Configure Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Create the Groq client
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Model to use (Llama 3.3 70B on Groq — free, fast, powerful)
MODEL = "llama-3.3-70b-versatile"
# Fallback model when primary hits daily token limit
FALLBACK_MODEL = "llama-3.1-8b-instant"

# System prompt for the chatbot
SYSTEM_PROMPT = """You are a helpful college enquiry chatbot for BVRIT (B V Raju Institute of Technology), Narsapur, Telangana, India.

Your role:
- Answer questions about the college based ONLY on the provided context
- Be friendly, professional, and informative
- If the context doesn't contain enough information, say so politely
- Do NOT make up information that is not in the context

CRITICAL RULES:
- Always quote EXACT data from the context: names, numbers, dates, phone numbers, email addresses, qualifications, designations, URLs
- When asked about a person, include ALL available details: qualifications, experience, contact info, publications, achievements
- When asked about a department/program, include ALL specific details: courses, faculty, facilities, eligibility
- Do NOT summarize or paraphrase factual data — reproduce it exactly as given
- If multiple pieces of context are relevant, combine them into a comprehensive answer
- Structure long answers with bullet points or sections for readability
- Include source URLs when available so users can visit the page for more info

DEPARTMENT DISAMBIGUATION:
BVRIT has several departments with similar-sounding names. Pay close attention to which EXACT department the user is asking about:
- AIDS / AI&DS = Artificial Intelligence and Data Science (URL contains /aids/)
- CSE-AI-ML / AI&ML = CSE – Artificial Intelligence and Machine Learning (URL contains /cse-ai-ml/)
- CSE-DS = CSE – Data Science (URL contains /cse-ds/)
- CSBS = Computer Science and Business Systems (URL contains /csbs/)
- CSE = Computer Science and Engineering (URL contains /cse/)
Only use information from the SPECIFIC department asked about. Do NOT mix up faculty or data from different departments.

FOR SHORT / QUICK QUESTIONS:
- Give a direct, concise answer first, then add relevant details
- For "who is the HOD/principal/dean?" — state the name and designation immediately
- For "what is [X]?" — give a brief definition/answer, then expand
"""


def build_prompt(context_chunks, user_question):
    """Build the prompt for the LLM with retrieved context."""
    context_text = "\n\n".join([
        f"[Source: {chunk.get('source', 'N/A')}]\n{chunk['text']}"
        for chunk in context_chunks
    ])
    
    prompt = f"""Answer the user's question using ONLY the following context from the college website.
IMPORTANT: Include ALL exact details (names, numbers, qualifications, contacts, dates) from the context. Do not omit or summarize factual information.
If the context doesn't contain relevant information, say "I don't have specific information about that, but you can check the college website at https://bvrit.ac.in for more details."

Context:
{context_text}

User Question: {user_question}

Provide a detailed, accurate answer with all specific information from the context:"""
    
    return prompt


def query_gemini(context_chunks, user_question):
    """Query Groq (Llama 3.3 70B) with context and user question."""
    if not GROQ_API_KEY or not client:
        return "Error: Groq API key not configured. Please set GROQ_API_KEY in the .env file. Get a free key at https://console.groq.com/keys"
    
    prompt = build_prompt(context_chunks, user_question)
    
    # Try primary model first, fall back to smaller model on rate limit
    for model_name in [MODEL, FALLBACK_MODEL]:
        try:
            print(f"  [LLM] Querying Groq ({model_name})...")
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2048,
                top_p=0.9,
            )
            
            answer = response.choices[0].message.content
            print(f"  [LLM] Response received ({len(answer)} chars) via {model_name}")
            return answer
            
        except Exception as e:
            error_msg = str(e)
            print(f"  [LLM] Error with {model_name}: {error_msg[:200]}")
            if ("rate_limit" in error_msg.lower() or "429" in error_msg) and model_name != FALLBACK_MODEL:
                print(f"  [LLM] Falling back to {FALLBACK_MODEL}...")
                continue
            if "auth" in error_msg.lower() or "api_key" in error_msg.lower():
                return "Error: Invalid Groq API key. Please check your GROQ_API_KEY in the .env file."
            return f"Error generating response: {error_msg}"
    
    return ("I'm currently experiencing high demand. Please wait a moment and try again. "
            "Your question was understood — the relevant information was found.")


def test_llm():
    """Test the LLM module with a sample query."""
    print("=" * 60)
    print("  LLM Module Test")
    print("=" * 60)
    
    # Sample context
    sample_context = [
        {
            "text": "Admissions at BVRIT are conducted through TS EAMCET counseling. Candidates must register in the state counselling process and select BVRIT during seat allotment.",
            "source": "https://bvrit.ac.in/admission-process/"
        },
        {
            "text": "BVRIT offers courses in Computer Science, Information Technology, Electronics, Mechanical, and Civil Engineering.",
            "source": "https://bvrit.ac.in/departments/"
        }
    ]
    
    question = "What is the admission process at BVRIT?"
    
    print(f"\nQuestion: {question}")
    print(f"\nGenerating response...\n")
    
    response = query_gemini(sample_context, question)
    print(f"Response:\n{response}")


if __name__ == "__main__":
    test_llm()
