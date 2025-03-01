import os
import faiss
import glob
import pickle
import time
import shutil
from typing import List, Optional, Dict, Any
import logging

from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.groq import Groq
from llama_index.llms.gemini import Gemini
import pymupdf4llm

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for managing the vector store."""
    
    def __init__(self):
        self.index = None
        self.vector_store = None
        self.embed_model = None
        self.llm = None
        self.node_parser = SentenceSplitter(
            chunk_size=512,  # Smaller chunks to avoid API size limits
            chunk_overlap=50
        )
        self.initialize_models()
        
        # Try to load existing index, create new one if it doesn't exist
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize index - load existing or create new if needed."""
        # Try to load existing index
        loaded_index = self.load_index()
        
        if loaded_index is not None:
            logger.info("Loaded existing vector index.")
            self.index = loaded_index
            return
        
        # If no index exists, create a new one
        logger.info("No existing vector index found. Creating new index from documents...")
        documents = self.load_documents_from_folder()
        
        if documents:
            logger.info(f"Found {len(documents)} documents. Creating index in batches...")
            self.create_index_in_batches(documents)
            logger.info("Index creation complete.")
        else:
            logger.warning("No documents found in the data folder. Index creation skipped.")
    
    def is_index_loaded(self) -> bool:
        """Check if the index is loaded."""
        return self.index is not None
    
    def is_index_on_disk(self) -> bool:
        """Check if the index exists on disk."""
        faiss_path = os.path.join(settings.VECTOR_DB_PATH, "faiss.index")
        metadata_path = os.path.join(settings.VECTOR_DB_PATH, "index_metadata.pkl")
        full_index_path = os.path.join(settings.VECTOR_DB_PATH, "full_index.pkl")
        
        return (os.path.exists(faiss_path) and os.path.exists(metadata_path)) or os.path.exists(full_index_path)
    
    def delete_index(self) -> bool:
        """Delete the index from disk."""
        try:
            if os.path.exists(settings.VECTOR_DB_PATH):
                shutil.rmtree(settings.VECTOR_DB_PATH)
            
            # Reset the index in memory
            self.index = None
            self.vector_store = None
            
            return True
        except Exception as e:
            logger.error(f"Error deleting index: {str(e)}")
            return False
    
    def initialize_models(self):
        """Initialize embedding and LLM models."""
        # Initialize embedding model
        self.embed_model = GeminiEmbedding(
            model_name=settings.EMBEDDING_MODEL, 
            api_key=settings.GOOGLE_API_KEY
        )
        
        # Configure global settings
        Settings.embed_model = self.embed_model
        
        # Initialize default LLM - try Groq first, fall back to Gemini
        try:
            self.llm = Groq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)
            Settings.llm = self.llm
        except Exception as e:
            logger.warning(f"Failed to initialize Groq: {str(e)}. Falling back to Gemini.")
            try:
                self.llm = Gemini(model=settings.GEMINI_MODEL, api_key=settings.GOOGLE_API_KEY)
                Settings.llm = self.llm
            except Exception as e2:
                logger.error(f"Failed to initialize any LLM. Please check your API keys. Error: {str(e2)}")
    
    def read_pdf(self, file_path: str) -> str:
        """Read PDF and convert to markdown."""
        try:
            return pymupdf4llm.to_markdown(file_path)
        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")
            return ""
    
    def load_documents_from_folder(self, folder_path: str = None) -> List[Document]:
        """Load documents from a folder."""
        if folder_path is None:
            folder_path = settings.DATA_DIR
        
        # Get all PDF files from the folder
        pdf_files = glob.glob(f"{folder_path}/*.pdf")
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {folder_path}!")
            return []
        
        # Read all PDF files and create document objects
        documents = []
        for file_path in pdf_files:
            print(f"Processing {file_path}...")
            text = self.read_pdf(file_path)
            if text:
                documents.append(Document(
                    text=text, 
                    metadata={"filename": os.path.basename(file_path)}
                ))
        
        return documents
    
    def create_index(self, nodes, use_nodes=False) -> VectorStoreIndex:
        """Create a vector index from nodes or documents."""
        # Create vector store
        faiss_index = faiss.IndexFlatL2(settings.EMBEDDING_DIMENSION)
        self.vector_store = FaissVectorStore(faiss_index=faiss_index)
        
        # Create and store index
        if use_nodes:
            self.index = VectorStoreIndex(
                nodes=nodes,
                vector_store=self.vector_store
            )
        else:
            self.index = VectorStoreIndex.from_documents(
                nodes,  # In this case, nodes are actually documents
                vector_store=self.vector_store
            )
        
        return self.index
    
    def create_index_in_batches(self, documents: List[Document], batch_size: int = 2) -> VectorStoreIndex:
        """Create a vector index from documents in batches to avoid memory issues."""
        if not documents:
            return None
        
        try:
            # Create a new FAISS index
            faiss_index = faiss.IndexFlatL2(settings.EMBEDDING_DIMENSION)
            
            # Create a vector store with the FAISS index
            self.vector_store = FaissVectorStore(faiss_index=faiss_index)
            
            # Process all documents by splitting them into smaller nodes first
            all_nodes = []
            for doc in documents:
                logger.info(f"Splitting document: {doc.metadata.get('filename', 'unknown')}")
                # Split document into smaller chunks to avoid API size limits
                nodes = self.node_parser.get_nodes_from_documents([doc])
                all_nodes.extend(nodes)
            
            logger.info(f"Created {len(all_nodes)} nodes from {len(documents)} documents")
            
            # Process nodes in small batches
            total_nodes = len(all_nodes)
            total_batches = (total_nodes + batch_size - 1) // batch_size
            
            # Initialize the index with the first batch
            first_batch = all_nodes[:batch_size]
            logger.info(f"Initializing index with first {len(first_batch)} nodes")
            
            # Create the initial index
            self.index = VectorStoreIndex(
                nodes=first_batch,
                vector_store=self.vector_store
            )
            
            # Save the initial index
            logger.info("Saving initial index...")
            self.save_index()
            
            # Process the rest in batches
            remaining_nodes = all_nodes[batch_size:]
            
            for i in range(0, len(remaining_nodes), batch_size):
                batch = remaining_nodes[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                
                logger.info(f"Processing batch {batch_num}/{total_batches-1} with {len(batch)} nodes...")
                
                try:
                    # Add nodes to the index
                    for node in batch:
                        self.index.insert_nodes([node])
                    
                    # Save after each batch to avoid losing progress
                    logger.info(f"Saving progress after batch {batch_num}...")
                    self.save_index()
                    
                    # Small delay to allow for resource cleanup
                    time.sleep(0.5)
                except Exception as batch_error:
                    logger.error(f"Error processing batch {batch_num}: {str(batch_error)}")
                    # Continue with next batch
                    continue
            
            return self.index
        except Exception as e:
            logger.error(f"Error creating index in batches: {str(e)}")
            # Try a simpler approach with even smaller batches if the batched approach fails
            logger.info("Trying alternative approach with smaller chunks...")
            try:
                # Use an even smaller chunk size
                self.node_parser = SentenceSplitter(
                    chunk_size=256,
                    chunk_overlap=20
                )
                
                # Process all documents again with smaller chunks
                all_nodes = []
                for doc in documents:
                    nodes = self.node_parser.get_nodes_from_documents([doc])
                    all_nodes.extend(nodes)
                
                # Create a new FAISS index
                faiss_index = faiss.IndexFlatL2(settings.EMBEDDING_DIMENSION)
                self.vector_store = FaissVectorStore(faiss_index=faiss_index)
                
                # Process in very small batches
                for i in range(0, len(all_nodes), 1):  # Process one node at a time
                    node_batch = [all_nodes[i]]
                    
                    if i == 0:
                        # Initialize index with first node
                        self.index = VectorStoreIndex(
                            nodes=node_batch,
                            vector_store=self.vector_store
                        )
                    else:
                        # Add node to existing index
                        self.index.insert_nodes(node_batch)
                    
                    # Save more frequently
                    if i % 5 == 0:
                        self.save_index()
                        time.sleep(0.5)
                
                # Final save
                self.save_index()
                return self.index
            except Exception as e2:
                logger.error(f"Error creating index with alternative approach: {str(e2)}")
                return None
    
    def save_index(self, path: str = None) -> bool:
        """Save the index to disk."""
        if path is None:
            path = settings.VECTOR_DB_PATH
        
        if not os.path.exists(path):
            os.makedirs(path)
        
        if self.index is None:
            return False
        
        try:
            # Save the entire index for backup
            try:
                with open(os.path.join(path, "full_index.pkl"), "wb") as f:
                    pickle.dump(self.index, f)
                logger.info("Successfully saved full index")
                return True
            except Exception as e:
                logger.warning(f"Could not save full index: {str(e)}")
                
                # Try component-based saving as fallback
                try:
                    # Get the underlying FAISS index
                    try:
                        faiss_index = self.vector_store._faiss_index
                    except (AttributeError, KeyError):
                        try:
                            faiss_index = self.index._vector_store._faiss_index
                        except (AttributeError, KeyError):
                            faiss_index = self.index._storage_context.vector_store._faiss_index
                    
                    # Save the FAISS index
                    faiss_path = os.path.join(path, "faiss.index")
                    faiss.write_index(faiss_index, faiss_path)
                    
                    # Save the metadata
                    metadata_dict = {}
                    try:
                        metadata_dict = self.vector_store._metadata_dict
                    except (AttributeError, KeyError):
                        try:
                            metadata_dict = self.index._vector_store._metadata_dict
                        except (AttributeError, KeyError):
                            metadata_dict = self.index._storage_context.vector_store._metadata_dict
                    
                    with open(os.path.join(path, "index_metadata.pkl"), "wb") as f:
                        pickle.dump(metadata_dict, f)
                    
                    logger.info("Successfully saved index components")
                    return True
                except Exception as e2:
                    logger.error(f"Error saving index components: {str(e2)}")
                    return False
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            return False
    
    def load_index(self, path: str = None) -> Optional[VectorStoreIndex]:
        """Load the index from disk."""
        if path is None:
            path = settings.VECTOR_DB_PATH
        
        # Try loading the full index first
        full_index_path = os.path.join(path, "full_index.pkl")
        if os.path.exists(full_index_path):
            try:
                with open(full_index_path, "rb") as f:
                    self.index = pickle.load(f)
                    # Also get the vector store from the index
                    try:
                        self.vector_store = self.index._vector_store
                    except AttributeError:
                        self.vector_store = self.index._storage_context.vector_store
                    return self.index
            except Exception as e:
                logger.error(f"Error loading full index: {str(e)}. Trying component-based loading...")
        
        # If full index loading fails, try component-based loading
        faiss_path = os.path.join(path, "faiss.index")
        metadata_path = os.path.join(path, "index_metadata.pkl")
        
        if not (os.path.exists(faiss_path) and os.path.exists(metadata_path)):
            return None
        
        try:
            # Load the FAISS index
            faiss_index = faiss.read_index(faiss_path)
            
            # Load the metadata
            with open(metadata_path, "rb") as f:
                metadata_dict = pickle.load(f)
            
            # Create the vector store
            self.vector_store = FaissVectorStore(
                faiss_index=faiss_index,
                metadata_dict=metadata_dict
            )
            
            # Create the index
            self.index = VectorStoreIndex.from_vector_store(self.vector_store)
            
            return self.index
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            return None
    
    def query(self, query_text: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Query the index."""
        if self.index is None:
            # Try to initialize the index one more time
            self._initialize_index()
            
            if self.index is None:
                return "Index not loaded. Please create or load an index first."
        
        # Build context from recent messages
        context_str = ""
        if chat_history:
            recent = chat_history[-10:]  # Last 5 interactions (10 messages)
            for i in range(0, len(recent), 2):
                if i+1 < len(recent):
                    context_str += f"### Previous Interaction:\n**User**: {recent[i]['content']}\n**Assistant**: {recent[i+1]['content']}\n\n"
        
        # Combine system prompt, context, and current question
        full_query = f"{settings.SYSTEM_PROMPT}\n\n{context_str}\n### New Question:\n{query_text}"
        
        # Try Groq first, fall back to Gemini
        try:
            Settings.llm = Groq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)
            query_engine = self.index.as_query_engine(response_mode="compact")
            response = query_engine.query(full_query)
            return str(response)
        except Exception as e:
            logger.warning(f"Groq query failed: {str(e)}. Falling back to Gemini.")
            try:
                Settings.llm = Gemini(model=settings.GEMINI_MODEL, api_key=settings.GOOGLE_API_KEY)
                query_engine = self.index.as_query_engine(response_mode="compact")
                response = query_engine.query(full_query)
                return str(response)
            except Exception as e2:
                logger.error(f"Both Groq and Gemini failed. Error: {str(e2)}")
                return f"Both Groq and Gemini failed. Error: {str(e2)}"

# Singleton instance
vector_store_service = VectorStoreService()
