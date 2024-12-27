def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Document Chat API is running"}

def test_upload_documents(client, mock_pdf_file, mock_vector_store, mock_embedding_service):
    # Create test file
    files = [
        ('files', ('test.pdf', mock_pdf_file, 'application/pdf'))
    ]
    
    response = client.post("/documents/upload", files=files)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    
    document = response.json()[0]
    assert document["name"] == "test.pdf"
    assert document["content_type"] == "application/pdf"
    assert document["embedding_status"] == "completed"

def test_chat_endpoint(client, mock_vector_store, mock_embedding_service):
    query_data = {
        "text": "What is the document about?",
        "document_ids": ["123"]
    }
    
    response = client.post("/chat", json=query_data)
    
    assert response.status_code == 200
    assert "response" in response.json()
    assert "Based on the documents" in response.json()["response"]
