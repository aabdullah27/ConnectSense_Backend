# ConnectSense RAG API

A Retrieval-Augmented Generation API for connectivity and telecommunications information built with FastAPI and LlamaIndex.

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
├── streamlit/                  # Streamlit frontend
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

- **Chat**:
  - `POST /chat`: Chat with the RAG system with chat history
  - `POST /chat/simple`: Simple chat endpoint for quick queries

### 3. LLM Integration

The system integrates with two language models:

- **Groq**: Primary LLM using the llama-3.3-70b-versatile model
- **Gemini**: Fallback LLM using the gemini-2.0-flash model

It also uses the Gemini embedding model for document vectorization.

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a .env file

Create a `.env` file in the root directory with the following content:

```
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
```

### 4. Add your PDF documents

Place your PDF documents in the `data` folder. The system will automatically index them on first run.

### 5. Run the API server

```bash
python run.py
```

The API will be available at http://localhost:8000

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

## API Endpoints

### Documentation

- `/docs` - Swagger UI documentation

### Index Management

- `GET /index/status` - Check the status of the vector index

### Chat

- `POST /chat` - Chat with the RAG system (with chat history)
- `POST /chat/simple` - Simple chat endpoint for quick queries

## Example Usage

### Check Index Status

```bash
curl -X GET http://localhost:8000/index/status
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/chat/simple \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the challenges of connectivity in South Asia?"}'
```

### Chat with History

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the challenges of connectivity in South Asia?",
    "chat_history": [
      {"role": "user", "content": "Hello, I want to learn about connectivity."},
      {"role": "assistant", "content": "Hello! I'd be happy to help you learn about connectivity. What specific aspects of connectivity are you interested in?"}
    ]
  }'
```

## Streamlit Frontend

A Streamlit frontend is available in the `streamlit` directory. To run it:

1. Install Streamlit:

```bash
pip install streamlit requests pandas
```

2. Run the Streamlit app:

```bash
cd streamlit
streamlit run app.py
```

The Streamlit app will be available at http://localhost:8501
