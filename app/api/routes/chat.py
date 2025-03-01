from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel

from app.models.chat import ChatRequest, ChatResponse, Message
from app.services.vector_store import vector_store_service

router = APIRouter()

async def validate_index():
    """Dependency to validate that the index is loaded."""
    if not vector_store_service.is_index_loaded():
        # Try to load the index
        index = vector_store_service.load_index()
        if index is None:
            raise HTTPException(
                status_code=400, 
                detail="Vector index not loaded. Please create or load an index first."
            )
    return True

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, index_loaded: bool = Depends(validate_index)):
    """
    Chat with the RAG system.
    
    This endpoint allows users to ask questions and get responses based on the indexed documents.
    """
    try:
        # Convert chat history to the format expected by the service
        chat_history = []
        if request.chat_history:
            for message in request.chat_history:
                chat_history.append({
                    "role": message.role,
                    "content": message.content
                })
        
        # Query the index
        response = vector_store_service.query(request.query, chat_history)
        
        # For now, we don't have a way to extract sources from the response
        # In a more advanced implementation, we could parse the response to extract sources
        return ChatResponse(
            response=response,
            sources=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying the index: {str(e)}")

class SimpleQuery(BaseModel):
    query: str

@router.post("/chat/simple", response_model=ChatResponse)
async def simple_chat(query_data: SimpleQuery, index_loaded: bool = Depends(validate_index)):
    """
    Simple chat endpoint that doesn't require chat history.
    
    This is a simplified version of the chat endpoint for quick queries.
    """
    try:
        # Query the index
        response = vector_store_service.query(query_data.query)
        
        return ChatResponse(
            response=response,
            sources=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying the index: {str(e)}")
