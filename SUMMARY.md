# ConnectSense RAG API - Project Summary

## Overview

ConnectSense RAG API is a Retrieval-Augmented Generation system built with FastAPI and LlamaIndex. It provides a powerful backend for querying a collection of PDF documents about connectivity and telecommunications topics. The system uses state-of-the-art embedding models and language models to provide accurate and contextually relevant answers to user queries.

## Architecture

The project follows a modular architecture with clear separation of concerns:

```
FastAPI_ConnectSense/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py         # Chat endpoints
│   │   │   ├── index.py        # Index management endpoints
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   └── __init__.py
│   ├── models/
│   │   ├── chat.py             # Pydantic models for API
│   │   └── __init__.py
│   ├── services/
│   │   ├── vector_store.py     # Vector store service
│   │   └── __init__.py
│   ├── main.py                 # FastAPI application
│   └── __init__.py
├── data/                       # PDF documents
├── vector_db/                  # Vector database storage
├── .env                        # Environment variables
├── .env.example                # Example environment variables
├── README.md                   # Project documentation
├── requirements.txt            # Dependencies
└── run.py                      # Script to run the application
```

## Key Components

### 1. Vector Store Service

The `VectorStoreService` in `app/services/vector_store.py` is the core of the RAG system. It handles:

- Loading PDF documents from the data folder
- Creating a vector index from the documents
- Processing documents in batches to handle large collections
- Saving and loading the vector index
- Querying the index with user questions

The service uses FAISS (Facebook AI Similarity Search) for efficient vector storage and retrieval. It automatically initializes on application startup, either by loading an existing index or creating a new one if needed.

### 2. API Routes

The API provides several endpoints:

- **Index Management**:
  - `GET /index/status`: Check the status of the vector index
  - `POST /index/create`: Create a new vector index
  - `GET /index/load`: Load an existing vector index

- **Chat**:
  - `POST /chat`: Chat with the RAG system with chat history
  - `POST /chat/simple`: Simple chat endpoint for quick queries

### 3. LLM Integration

The system integrates with two language models:

- **Groq**: Primary LLM using the llama-3.3-70b-versatile model
- **Gemini**: Fallback LLM using the gemini-2.0-flash model

It also uses the Gemini embedding model for document vectorization.

## Technical Features

### Automatic Index Creation

The system automatically creates a vector index on first run:

1. Checks if an index exists in the vector_db folder
2. If not, loads all PDFs from the data folder
3. Processes documents in batches to avoid memory issues
4. Saves the index for future use

### Batch Processing

To handle large document collections efficiently, the system:

1. Processes the first document to initialize the index
2. Processes remaining documents in small batches (default: 3 documents per batch)
3. Saves progress after each batch to avoid losing work
4. Includes small delays between batches to allow for resource cleanup

### Error Handling and Fallbacks

The system includes robust error handling:

- Tries Groq LLM first, falls back to Gemini if Groq fails
- Handles PDF parsing errors gracefully
- Provides clear error messages in API responses

## Usage Workflow

1. **Setup**: Install dependencies and set API keys in .env file
2. **Add Documents**: Place PDF documents in the data folder
3. **Run Application**: Start the FastAPI server with `python run.py`
4. **First Run**: System automatically creates vector index from PDFs
5. **Query**: Use the chat endpoints to ask questions about the documents
6. **Subsequent Runs**: System loads the existing index automatically

## API Models

The API uses Pydantic models for request and response validation:

- `Message`: Chat message with role and content
- `ChatRequest`: Chat request with query and optional chat history
- `ChatResponse`: Chat response with assistant's response and sources
- `IndexResponse`: Index operation response with status, message, and document count

## Configuration

The application configuration in `app/core/config.py` includes:

- API keys for language models
- Model names and parameters
- System prompt for the chatbot
- Vector database settings

## Conclusion

ConnectSense RAG API provides a powerful and flexible backend for building AI-powered applications that can answer questions about connectivity and telecommunications topics. The system is designed to be easy to set up and use, with automatic index creation and robust error handling.
