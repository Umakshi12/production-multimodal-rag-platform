"""Production-ready data ingestion pipeline"""

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from logger import get_logger
from config import (
    VECTOR_DB_PATH, DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP,
    OPENAI_API_KEY, EMBEDDING_MODEL
)
from web_scraper import load_website_data
from document_processor import DocumentProcessor

logger = get_logger(__name__)


class DataIngestionPipeline:
    """Complete data ingestion and vector DB creation"""
    
    def __init__(self):
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP
        self.vector_db_path = VECTOR_DB_PATH
        self.data_dir = DATA_DIR
        
        # Initialize embeddings
        # self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
    def load_data(self):
        """Load data from all sources"""
        all_documents = []
        
        logger.info("=" * 60)
        logger.info("STARTING DATA INGESTION PIPELINE")
        logger.info("=" * 60)
        
        # 1. Load website data
        try:
            logger.info("\nLoading website data...")
            website_docs = load_website_data()
            all_documents.extend(website_docs)
            logger.info(f"Website: {len(website_docs)} documents")
        except Exception as e:
            logger.error(f"Error loading website: {e}")
        
        # 2. Load company documents
        try:
            logger.info("\nLoading company documents...")
            processor = DocumentProcessor()
            doc_files = processor.process_all_documents(self.data_dir)
            all_documents.extend(doc_files)
            logger.info(f"Company Documents: {len(doc_files)} documents")
        except Exception as e:
            logger.error(f"Error loading company documents: {e}")
        
        logger.info(f"\nTotal documents loaded: {len(all_documents)}")
        return all_documents
    
    def chunk_documents(self, documents):
        """Split documents into chunks"""
        logger.info(f"\nChunking documents (size={self.chunk_size}, overlap={self.chunk_overlap})...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        splits = text_splitter.split_documents(documents)
        logger.info(f"Created {len(splits)} chunks")
        
        return splits
    
    def create_vector_db(self, documents):
        """Create and persist vector database"""
        logger.info(f"\nCreating vector database at {self.vector_db_path}...")
        
        # Remove existing DB if it exists
        import shutil
        if os.path.exists(self.vector_db_path):
            logger.info("Removing existing vector database...")
            shutil.rmtree(self.vector_db_path)
        
        # Create new vector DB
        try:
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.vector_db_path
            )
            logger.info(f"Vector database created successfully")
            logger.info(f"Stored {len(documents)} documents in ChromaDB")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error creating vector database: {e}")
            raise
    
    def run(self):
        """Execute complete ingestion pipeline"""
        try:
            # Load all data
            documents = self.load_data()
            
            if not documents:
                logger.error(" No documents loaded!")
                return False
            
            # Split into chunks
            splits = self.chunk_documents(documents)
            
            if not splits:
                logger.error("No chunks created!")
                return False
            
            # Create vector DB
            self.create_vector_db(splits)
            
            logger.info("\n" + "=" * 60)
            logger.info("DATA INGESTION COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"Summary:")
            logger.info(f"   - Total Documents: {len(documents)}")
            logger.info(f"   - Total Chunks: {len(splits)}")
            logger.info(f"   - Vector DB Location: {self.vector_db_path}")
            logger.info("=" * 60 + "\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return False


if __name__ == "__main__":
    pipeline = DataIngestionPipeline()
    success = pipeline.run()
    exit(0 if success else 1)
