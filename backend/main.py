import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add project root directory to python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()

from backend.models import QueryRequest, QueryResponse
from backend.rag.retriever import Retriever
from backend.rag.answer_engine import AnswerEngine

app = FastAPI(
    title="RuleGuard AI Backend",
    description="Evidence-Based University Regulation Assistant API",
    version="1.0.0"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = None
answer_engine = None

@app.on_event("startup")
def startup_event():
    global retriever, answer_engine
    print("Initializing RuleGuard AI Backend...")
    try:
        retriever = Retriever()
        answer_engine = AnswerEngine()
        print("Retriever and AnswerEngine successfully loaded.")
    except Exception as e:
        print(f"Startup Warning: {e}")

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "RuleGuard AI Backend",
        "index_loaded": retriever.loaded if retriever else False
    }

@app.post("/ask", response_model=QueryResponse)
def ask_question(payload: QueryRequest):
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question string cannot be empty.")

    if retriever is None or not retriever.loaded:
        raise HTTPException(
            status_code=503,
            detail="Vector index is not loaded. Please execute 'python backend/scripts/build_index.py' first."
        )

    try:
        # Retrieve top relevant passages using cosine similarity
        retrieved_passages = retriever.retrieve(payload.question, top_k=6)
        
        # Process answer classification (ANSWERED, NOT_COVERED, CONFLICT)
        response = answer_engine.process_query(payload.question, retrieved_passages)
        return response
    except Exception as e:
        print(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
