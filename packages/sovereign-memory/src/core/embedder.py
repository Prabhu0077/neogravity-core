"""
Local Embedding Specialist

Replaces cloud Gemini/OpenAI embeddings with local sentence-transformers.
Model: all-MiniLM-L6-v2 (22M params, 384-dim, ~90MB RAM, CPU-only).
"""

import logging
from typing import Union

from src.mcp.config import MODELS

logger = logging.getLogger(__name__)

# Lazy-loaded singleton — model loads on first call, not import
_model = None


def _get_model():
    """Lazy-load the sentence-transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model: {MODELS.embedding_model}...")
        _model = SentenceTransformer(MODELS.embedding_model)
        logger.info(
            f"Embedding model loaded. Dim={_model.get_sentence_embedding_dimension()}"
        )
    return _model


def embed_text(text: str) -> list[float]:
    """
    Embed a single text string into a 384-dim vector.
    
    First call triggers model download (~90MB) if not cached.
    Subsequent calls use the cached model instance.
    """
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_batch(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """
    Embed a batch of texts efficiently.
    
    Uses sentence-transformers' internal batching for GPU/CPU optimization.
    """
    model = _get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 50,
    )
    return embeddings.tolist()


def get_embedding_dim() -> int:
    """Return the embedding dimension (384 for MiniLM-L6-v2)."""
    return MODELS.embedding_dim


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two normalized vectors.
    Since we normalize embeddings, this is just the dot product.
    """
    import numpy as np
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b))
