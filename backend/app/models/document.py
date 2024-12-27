from pydantic import BaseModel
from typing import List, Optional

class Document(BaseModel):
    id: str
    name: str
    content_type: str
    size: int
    embedding_status: str = "pending"

class Query(BaseModel):
    text: str
    document_ids: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str

