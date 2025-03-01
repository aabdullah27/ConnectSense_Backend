# ConnectSense RAG API

A Retrieval-Augmented Generation API for connectivity and telecommunications information built with FastAPI and LlamaIndex.

## Features

- Automatic PDF document indexing using FAISS vector store
- Batch processing to handle large document collections
- RAG-powered question answering
- Chat history support for contextual responses
- Swagger UI documentation

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

## How it Works

- On first run, the system will automatically create a vector index from all PDFs in the `data` folder
- The documents are processed in batches to avoid memory issues
- The vector index is saved to the `vector_db` directory
- On subsequent runs, the system will load the existing index from the `vector_db` directory
- If you add new documents to the `data` folder, you can trigger a reindex by deleting the `vector_db` folder

## API Endpoints

### Documentation

- `/docs` - Swagger UI documentation

### Index Management

- `GET /index/status` - Check the status of the vector index
- `POST /index/create` - Create a new vector index from documents in the data folder
- `GET /index/load` - Load an existing vector index

### Chat

- `POST /chat` - Chat with the RAG system (with chat history)
- `POST /chat/simple?query=your_question` - Simple chat endpoint for quick queries

## Example Usage

### Check Index Status

```bash
curl -X GET http://localhost:8000/index/status
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/chat/simple?query=What%20are%20the%20challenges%20of%20connectivity%20in%20South%20Asia%3F
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
