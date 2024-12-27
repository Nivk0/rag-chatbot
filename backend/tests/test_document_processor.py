from ..app.services.document_processor import DocumentProcessor


def test_document_processor_pdf():
    processor = DocumentProcessor()
    
    # Test PDF processing
    pdf_content = b"mock PDF content"
    result = processor.process_document(pdf_content, "test.pdf", "application/pdf")
    
    assert "chunks" in result
    assert "embeddings" in result
    assert "filename" in result
    assert "num_chunks" in result
    assert result["filename"] == "test.pdf"

def test_document_processor_docx():
    processor = DocumentProcessor()
    
    # Test DOCX processing
    docx_content = b"mock DOCX content"
    result = processor.process_document(
        docx_content,
        "test.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    
    assert "chunks" in result
    assert "embeddings" in result
    assert "filename" in result
    assert "num_chunks" in result
    assert result["filename"] == "test.docx"