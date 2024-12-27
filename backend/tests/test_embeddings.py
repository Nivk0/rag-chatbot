from ..app.services.embeddings import EmbeddingService


def test_embedding_service():
    service = EmbeddingService("BAAI/bge-small-en")
    texts = ["This is a test document"]
    
    embeddings = service.get_embeddings(texts)
    assert len(embeddings) == 1
    assert len(embeddings[0]) == 384