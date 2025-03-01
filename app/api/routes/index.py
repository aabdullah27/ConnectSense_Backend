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
            message="Vector index is not loaded. Please wait for the system to initialize.",
            document_count=0
        )
