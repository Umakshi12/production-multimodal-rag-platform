"""FastAPI endpoints for the RAG chatbot (optional REST API)"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from rag_chatbot import create_chatbot
from logger import get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Oceania RAG Chatbot API",
    description="REST API for Oceanic6 Solutionz AI Assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "extracted_images")
DATA_DIR_PATH = os.path.join(BASE_DIR, "company_data")

# Mount static directories with absolute paths
app.mount("/extracted_images", StaticFiles(directory=IMAGE_DIR), name="extracted_images")
app.mount("/company_data", StaticFiles(directory=DATA_DIR_PATH), name="company_data")

# Initialize chatbot
try:
    chatbot = create_chatbot()
except Exception as e:
    logger.error(f"Failed to initialize chatbot: {e}")
    chatbot = None


# Request/Response models
class ChatRequest(BaseModel):
    query: str
    include_sources: bool = True
    image_base64: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    images: List[str]
    retrieved_chunks: int


class HistoryRequest(BaseModel):
    queries: List[str]


class RetrievalDetailsResponse(BaseModel):
    query: str
    num_retrieved: int
    documents: List[dict]


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if chatbot is ready"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    return {"status": "healthy", "chatbot": "ready"}


# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a chat message and get a response"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        response = chatbot.chat(request.query, image_base64=request.image_base64, include_sources=request.include_sources)
        # Sanitize image paths for web
        if "images" in response:
            response["images"] = [img.replace("\\", "/") for img in response["images"]]
        return ChatResponse(**response)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Batch chat endpoint
@app.post("/batch-chat", response_model=List[ChatResponse])
async def batch_chat(request: HistoryRequest):
    """Process multiple queries at once"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        responses = chatbot.batch_chat(request.queries)
        return [ChatResponse(**r) for r in responses]
    except Exception as e:
        logger.error(f"Error in batch chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Retrieval details endpoint
@app.get("/retrieval-details/{query}", response_model=RetrievalDetailsResponse)
async def get_retrieval_details(query: str):
    """Get detailed retrieval information for a query"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        details = chatbot.get_retrieval_details(query)
        return RetrievalDetailsResponse(**details)
    except Exception as e:
        logger.error(f"Error getting retrieval details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Conversation history endpoint
@app.get("/history")
async def get_history():
    """Get conversation history"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        return {"history": chatbot.get_history()}
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Clear history endpoint
@app.post("/clear-history")
async def clear_history():
    """Clear conversation history"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        chatbot.clear_history()
        return {"status": "success", "message": "History cleared"}
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for streaming
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with streaming"""
    await websocket.accept()
    
    if chatbot is None:
        await websocket.send_text(json.dumps({"error": "Chatbot not initialized"}))
        await websocket.close()
        return
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            request = json.loads(data)
            query = request.get("query", "")
            
            if not query:
                await websocket.send_text(json.dumps({"error": "Empty query"}))
                continue
            
            # Stream response
            full_response = ""
            for token in chatbot.stream_chat(query):
                full_response += token
                await websocket.send_text(json.dumps({
                    "type": "token",
                    "content": token
                }))
            
            # Send completion
            await websocket.send_text(json.dumps({
                "type": "complete",
                "content": full_response
            }))
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({"error": str(e)}))
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Oceania RAG Chatbot API...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
