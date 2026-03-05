"""
Surprise Detection

Detects contradictions when new information conflicts with existing knowledge.
If a new chunk has high cosine similarity (similar topic) but different content,
it raises a surprise flag — preventing silent overwrite of decisions.

Example: "salary target: $80k" vs "salary target: $200k" → SURPRISE flagged.
"""

import logging

from src.mcp.config import SURPRISE
from src.core import embedder
from src.stores.chroma_store import ChromaStore

logger = logging.getLogger(__name__)


def check_surprise(
    new_content: str,
    new_embedding: list[float],
    chroma: ChromaStore,
    threshold: float = None,
) -> list[dict]:
    """
    Check if new content contradicts existing knowledge.
    
    A surprise is detected when:
    1. An existing chunk has cosine similarity > threshold with the new content
    2. BUT the text content is substantially different (not a near-duplicate)
    
    Args:
        new_content: The new text to check.
        new_embedding: Pre-computed embedding of the new text.
        chroma: The ChromaStore to search for conflicts.
        threshold: Similarity threshold for flagging (default from config).
    
    Returns:
        List of conflicting chunk dicts with surprise metadata.
    """
    threshold = threshold or SURPRISE.cosine_threshold
    
    # Search for high-similarity chunks across HOT and WARM
    similar = chroma.query(
        query_embedding=new_embedding,
        top_k=5,
    )
    
    surprises = []
    for result in similar:
        similarity = 1 - result.get("distance", 1)
        existing_content = result.get("content", "")
        
        # High similarity (same topic) but different content → surprise
        if similarity >= threshold and not _is_near_duplicate(new_content, existing_content):
            surprises.append({
                "conflicting_id": result["id"],
                "conflicting_content": existing_content[:200],
                "similarity": round(similarity, 4),
                "tier": result.get("tier", "unknown"),
                "source": result.get("metadata", {}).get("source", "unknown"),
            })
            
            # Flag the existing chunk as having a surprise
            chroma.flag_surprise(
                chunk_id=result["id"],
                tier=result.get("tier", "hot"),
                conflicting_id="new_ingestion",
            )
    
    if surprises:
        logger.warning(
            f"SURPRISE DETECTED: {len(surprises)} potential contradictions found. "
            f"Highest similarity: {surprises[0]['similarity']}"
        )
    
    return surprises


def _is_near_duplicate(text_a: str, text_b: str, duplicate_threshold: float = 0.95) -> bool:
    """
    Check if two texts are near-duplicates (the same content with minor edits).
    
    Near-duplicates should NOT trigger surprise — they're just updates.
    Uses a simple character-level ratio to avoid expensive embedding re-computation.
    """
    # Simple heuristic: if texts share > 95% of characters, it's a near-duplicate
    shorter = min(len(text_a), len(text_b))
    if shorter == 0:
        return False
    
    # Count matching characters in sequence (simplified diff)
    matches = sum(1 for a, b in zip(text_a, text_b) if a == b)
    ratio = matches / shorter
    
    return ratio >= duplicate_threshold
