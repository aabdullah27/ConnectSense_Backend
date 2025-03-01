import os
import glob
import logging
from fastapi import APIRouter, HTTPException
from app.models.chat import IndexResponse
from app.services.vector_store import vector_store_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/status", response_model=IndexResponse)
async def get_index_status():
    """Check if the index exists."""
    # Check if vector index exists
    if vector_store_service.is_index_loaded():
        # Count documents in data folder
        pdf_files = glob.glob(f"{settings.DATA_DIR}/*.pdf")
        return IndexResponse(
            status="success",
            message="Vector index is loaded and ready for queries.",
            document_count=len(pdf_files)
        )
    else:
        return IndexResponse(
            status="error",
            message="Vector index is not loaded. Please create an index first.",
            document_count=0
        )

@router.post("/create", response_model=IndexResponse)
async def create_index():
    """Create a new vector index from the documents in the data folder."""
    # Check if index already exists
    if vector_store_service.is_index_loaded():
        # Count documents in data folder
        pdf_files = glob.glob(f"{settings.DATA_DIR}/*.pdf")
        return IndexResponse(
            status="info",
            message="Index already exists. It will be used automatically.",
            document_count=len(pdf_files)
        )
    
    # Load documents
    documents = vector_store_service.load_documents_from_folder()
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found in the data folder.")
    
    # Create index in batches
    try:
        vector_store_service.create_index_in_batches(documents)
        return IndexResponse(
            status="success",
            message=f"Successfully created vector index from {len(documents)} documents.",
            document_count=len(documents)
        )
    except Exception as e:
        logger.error(f"Error creating index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating index: {str(e)}")

@router.get("/load", response_model=IndexResponse)
async def load_index():
    """Load an existing vector index."""
    # Check if index exists
    if not vector_store_service.is_index_loaded():
        raise HTTPException(status_code=404, detail="No index found. Please create an index first.")
    
    # Load index
    try:
        vector_store_service.load_index()
        # Count documents in data folder
        pdf_files = glob.glob(f"{settings.DATA_DIR}/*.pdf")
        
        return IndexResponse(
            status="success",
            message="Successfully loaded vector index.",
            document_count=len(pdf_files)
        )
    except Exception as e:
        logger.error(f"Error loading index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading index: {str(e)}")

@router.delete("/", response_model=IndexResponse)
async def delete_index():
    """Delete the existing vector index."""
    # Check if index exists
    if not vector_store_service.is_index_loaded():
        return IndexResponse(
            status="info",
            message="No index found. Nothing to delete.",
        )
    
    # Delete index files
    try:
        vector_store_service.delete_index()
        return IndexResponse(
            status="success",
            message="Successfully deleted vector index.",
        )
    except Exception as e:
        logger.error(f"Error deleting index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting index: {str(e)}")
