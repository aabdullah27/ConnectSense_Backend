import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import glob

from app.core.config import settings
from app.api.routes import chat, index
from app.services.vector_store import vector_store_service

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url=None,
    redoc_url=None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(index.router, prefix="/index", tags=["Index"])
app.include_router(chat.router, tags=["Chat"])

# Custom Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        routes=app.routes,
    )

@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "status": "API is running",
        "docs": "/docs",
        "index_status": "Loaded" if vector_store_service.is_index_loaded() else "Not loaded"
    }

# Startup event to ensure vector index is initialized
@app.on_event("startup")
async def startup_event():
    """Ensure vector index is initialized when the application starts."""
    try:
        # Try to load the index if it exists
        if not vector_store_service.is_index_loaded():
            # If index doesn't exist, try to create it from documents
            documents = vector_store_service.load_documents_from_folder()
            if documents:
                print(f"Creating index from {len(documents)} documents...")
                vector_store_service.create_index_in_batches(documents)
                print("Index created successfully.")
            else:
                print("No documents found. Index not created.")
        else:
            # Count PDF files in data directory
            pdf_files = glob.glob(f"{settings.DATA_DIR}/*.pdf")
            print(f"Vector index initialized. Found {len(pdf_files)} PDF documents in data directory.")
    except Exception as e:
        print(f"Error initializing vector index: {str(e)}")
        print("WARNING: Vector index not initialized. Queries may fail.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
