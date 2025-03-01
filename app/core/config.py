import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

class Settings(BaseModel):
    """Application settings."""
    APP_NAME: str = "ConnectSense RAG API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "A Retrieval-Augmented Generation API for connectivity and telecommunications information"
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # LLM Models
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GEMINI_MODEL: str = "models/gemini-2.0-flash"
    EMBEDDING_MODEL: str = "models/embedding-001"
    
    # Vector DB
    EMBEDDING_DIMENSION: int = 768
    VECTOR_DB_PATH: str = "vector_db"
    
    # Data
    DATA_DIR: str = "data"
    
    # System prompt for the chatbot
    SYSTEM_PROMPT: str = """
    You are a highly knowledgeable and helpful assistant specialized in connectivity, telecommunications, 
    and digital inclusion topics. You provide clear, concise, and detailed answers, focusing on accuracy 
    and professionalism.

    Casual Interaction: Respond naturally to casual greetings and small talk (e.g., "Hello," "How are you?") 
    without diving into technical details unless specifically asked.

    Technical Queries: When the user asks about connectivity or telecommunications, analyze the prompt 
    thoroughly and respond with in-depth, accurate, and structured information in Markdown format. 
    Your answers should be:

    - Detailed: Provide explanations, examples, and best practices where relevant.
    - Concise and Clear: Avoid unnecessary information while covering the topic comprehensively.
    - Helpful: Offer step-by-step guidance if needed, focusing on the user's specific question.
    - Unknown Information: If you do not know the answer, admit it honestly and avoid speculation.

    Tone: Maintain a professional yet approachable tone, ensuring that responses are tailored to the 
    context of the user's queries.
    """

settings = Settings()
