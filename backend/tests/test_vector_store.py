from ..app.services.vector_store import VectorStore


def test_vector_store_initialization():
    store = VectorStore()
    assert store.client is not None

def test_vector_store_add_documents():
    store = VectorStore()
    embeddings = [[0.1] * 384]  # Match BGE-small-en dimension
    metadata = [{"chunk_index": 0, "filename": "test.pdf", "content": "test content"}]
    
    # Should not raise any exceptions
    store.add_documents(embeddings, metadata)

def test_vector_store_search():
    store = VectorStore()
    query_vector = [0.1] * 384  # Match BGE-small-en dimension
    
    results = store.search(query_vector, limit=5)
    assert isinstance(results, list)