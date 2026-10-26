from pgvector.django import CosineDistance
from sentence_transformers import SentenceTransformer

from .models import DocumentChunk

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def retrieve(question, k=4):
    query_vector = get_model().encode(question, normalize_embeddings=True).tolist()
    chunks = (
        DocumentChunk.objects
        .annotate(distance=CosineDistance("embedding", query_vector))
        .order_by("distance")[:k]
    )
    return [
        {
            "source": c.source,
            "page": c.page,
            "chunk_index": c.chunk_index,
            "text": c.text,
            "distance": float(c.distance),
        }
        for c in chunks
    ]