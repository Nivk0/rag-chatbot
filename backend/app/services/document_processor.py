from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
import PyPDF2
import docx
import io
from .embeddings import EmbeddingService
from ..core.config import settings  

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.embedding_service = EmbeddingService(settings.EMBEDDINGS_MODEL)
    
    def extract_text(self, content: bytes, content_type: str) -> str:
        if content_type == 'application/pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ' '.join(page.extract_text() for page in pdf_reader.pages)
        elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = docx.Document(io.BytesIO(content))
            text = ' '.join(paragraph.text for paragraph in doc.paragraphs)
        elif content_type == 'text/plain':
            text = content.decode('utf-8')
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
        return text
    
    def process_document(self, content: bytes, filename: str, content_type: str) -> Dict:
        # Extract text from document
        text = self.extract_text(content, content_type)
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Generate embeddings
        embeddings = self.embedding_service.get_embeddings(chunks)
        
        return {
            "chunks": chunks,
            "embeddings": embeddings,
            "filename": filename,
            "num_chunks": len(chunks)
        }