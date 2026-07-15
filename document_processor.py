"""Document processors for PDF, DOCX, and other file types"""

import os
import base64
from pathlib import Path
from typing import List
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image
from io import BytesIO
from langchain_community.document_loaders import Docx2txtLoader, TextLoader
from langchain_core.documents import Document
# from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from logger import get_logger
from config import IMAGE_OUTPUT_DIR, MISTRAL_AI_API_KEY, MISTRAL_AI_MODEL
logger = get_logger(__name__)

class ImageDescriber:
    """Uses vision AI to describe images"""
    
    def __init__(self):
        # self.model = ChatOpenAI(model="gpt-5-mini", max_tokens=500)
        self.model = ChatMistralAI(model=MISTRAL_AI_MODEL, max_tokens=500, api_key=MISTRAL_AI_API_KEY)
        
    def describe(self, image_bytes):
        """Generate detailed description of image"""
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            msg = self.model.invoke([
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text", 
                            "text": """Describe this image in detail. Include:
- If it's a product: color, texture, pattern, size, any visible specifications
- If it's a table: summarize the data, key metrics, column headers
- If it's a diagram: explain what it shows
- Any text visible in the image"""
                        },
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ])
            return msg.content
            
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return "Unable to describe image"


class PDFProcessor:
    """Process PDF files for text and images"""
    
    def __init__(self):
        self.image_describer = ImageDescriber()
        os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
        
    def extract_tables_from_page(self, page) -> str:
        """Extract tables from PDF page and convert to Markdown"""
        try:
            tables = page.extract_tables()
            markdown_tables = []
            
            for table in tables:
                if not table:
                    continue
                    
                # Clean None values
                cleaned_table = [[str(cell) if cell is not None else "" for cell in row] for row in table]
                
                if len(cleaned_table) > 0:
                    # Build Markdown table
                    md = "\n| " + " | ".join(cleaned_table[0]) + " |\n"
                    md += "| " + " | ".join(["---"] * len(cleaned_table[0])) + " |\n"
                    for row in cleaned_table[1:]:
                        md += "| " + " | ".join(row) + " |\n"
                    markdown_tables.append(md)
                    
            return "\n".join(markdown_tables)
            
        except Exception as e:
            logger.warning(f"Error extracting tables: {e}")
            return ""
    
    def process_pdf(self, file_path: str) -> List[Document]:
        """Process PDF and extract text, tables, and images"""
        logger.info(f"Processing PDF: {file_path}")
        documents = []
        
        try:
            doc = fitz.open(file_path)
            pdf_plumber_doc = pdfplumber.open(file_path)
            
            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    plumber_page = pdf_plumber_doc.pages[page_num]
                    
                    # Extract text
                    raw_text = page.get_text()
                    
                    # Extract tables
                    table_text = self.extract_tables_from_page(plumber_page)
                    
                    # Combine content
                    page_content = raw_text
                    if table_text:
                        page_content += "\n\n## STRUCTURED DATA (TABLES):\n" + table_text
                    
                    if page_content.strip():
                        documents.append(Document(
                            page_content=page_content,
                            metadata={
                                "source": f"{os.path.basename(file_path)} (Page {page_num + 1})",
                                "source_type": "pdf_text",
                                "file_type": "pdf"
                            }
                        ))
                    
                    # Extract images
                    self._extract_images(doc, file_path, page_num, documents)
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_num}: {e}")
                    
            pdf_plumber_doc.close()
            doc.close()
            logger.info(f"Extracted {len(documents)} chunks from PDF")
            
        except Exception as e:
            logger.error(f"Error opening PDF {file_path}: {e}")
            
        return documents
    
    def _extract_images(self, doc, file_path: str, page_num: int, documents: List[Document]):
        """Extract and describe images from PDF page"""
        try:
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Skip very small images (likely icons)
                    if len(image_bytes) < 5000:
                        continue
                    
                    # Save image
                    image_filename = f"{Path(file_path).stem}_p{page_num}_img{img_index}.{image_ext}"
                    local_image_path = os.path.join(IMAGE_OUTPUT_DIR, image_filename)
                    
                    with open(local_image_path, "wb") as f:
                        f.write(image_bytes)
                    
                    # Describe image
                    logger.info(f"Analyzing image: {image_filename}")
                    description = self.image_describer.describe(image_bytes)
                    
                    documents.append(Document(
                        page_content=f"[IMAGE DESCRIPTION]\n{description}",
                        metadata={
                            "source": f"{os.path.basename(file_path)} (Page {page_num + 1})",
                            "source_type": "pdf_image",
                            "image_path": local_image_path,
                            "file_type": "pdf"
                        }
                    ))
                    
                except Exception as e:
                    logger.warning(f"Error extracting image {img_index}: {e}")
                    
        except Exception as e:
            logger.warning(f"Error in image extraction: {e}")


class DocumentProcessor:
    """Process various document types"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        
    def process_docx(self, file_path: str) -> List[Document]:
        """Process Word documents"""
        logger.info(f"Processing DOCX: {file_path}")
        try:
            loader = Docx2txtLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata['source_type'] = 'docx'
                doc.metadata['file_type'] = 'docx'
            logger.info(f"Processed DOCX: {len(docs)} documents")
            return docs
        except Exception as e:
            logger.error(f"Error processing DOCX {file_path}: {e}")
            return []
    
    def process_txt(self, file_path: str) -> List[Document]:
        """Process text files"""
        logger.info(f"Processing TXT: {file_path}")
        try:
            loader = TextLoader(file_path)
            docs = loader.load()
            for doc in docs:
                doc.metadata['source_type'] = 'text'
                doc.metadata['file_type'] = 'txt'
            return docs
        except Exception as e:
            logger.error(f"Error processing TXT {file_path}: {e}")
            return []
    
    def process_all_documents(self, data_dir: str) -> List[Document]:
        """Process all documents in a directory"""
        all_docs = []
        
        logger.info(f"Processing documents from: {data_dir}")
        
        if not os.path.exists(data_dir):
            logger.warning(f"Data directory not found: {data_dir}")
            return all_docs
        
        for file_path in Path(data_dir).glob("**/*"):
            if not file_path.is_file():
                continue
                
            try:
                if file_path.suffix.lower() == ".pdf":
                    all_docs.extend(self.pdf_processor.process_pdf(str(file_path)))
                elif file_path.suffix.lower() == ".docx":
                    all_docs.extend(self.process_docx(str(file_path)))
                elif file_path.suffix.lower() == ".txt":
                    all_docs.extend(self.process_txt(str(file_path)))
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        logger.info(f"Total documents processed: {len(all_docs)}")
        return all_docs
