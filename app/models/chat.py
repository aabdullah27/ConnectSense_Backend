from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    """Chat request model."""
    query: str = Field(..., description="User query/question")
    chat_history: Optional[List[Message]] = Field(default=[], description="Chat history for context")
    
class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Assistant's response")
    sources: Optional[List[str]] = Field(default=[], description="Sources used for the response")

class IndexResponse(BaseModel):
    """Index response model."""
    status: str = Field(..., description="Status of the indexing operation")
    message: str = Field(..., description="Detailed message about the indexing operation")
    document_count: int = Field(..., description="Number of documents indexed")
