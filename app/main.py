from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from models import (
    SearchRequest, SearchResponse, ChatRequest, ChatResponse,
    BNSSection, BNSChapter
)
from bns_chain import search_bns, get_all_sections, get_section_by_number, chat_bns
from vector_store import get_embeddings

app = FastAPI(
    title="BNS Legal Assistant",
    description="AI-powered tool to search and explore the Bharatiya Nyaya Sanhita, 2023",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "BNS Legal Assistant API",
        "version": "1.0.0",
        "disclaimer": "This tool provides legal information, not legal advice. Consult a qualified advocate for legal matters."
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/search", response_model=SearchResponse)
async def search_bns_endpoint(request: SearchRequest):
    try:
        result = search_bns(
            query=request.query,
            chapter_filter=request.chapter_filter,
            section_filter=request.section_filter,
            limit=request.limit
        )
        return SearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sections")
async def get_sections_endpoint():
    try:
        result = get_all_sections()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sections/{section_number}")
async def get_section_endpoint(section_number: str):
    try:
        result = get_section_by_number(section_number)
        if not result:
            raise HTTPException(status_code=404, detail="Section not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        result = chat_bns(messages, request.context_sections)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
