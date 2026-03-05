"""
Temporal Decay Scoring

Applies exponential decay weighting to retrieval results so that
recent information outranks old information.

Formula: relevance = cosine_similarity × exp(-λ × days_since_access)

With λ = 0.05:
  1 day  → 0.95 (nearly full weight)
  7 days → 0.70
  14 days → 0.50
  30 days → 0.22
  60 days → 0.05
"""

import math
import time
import logging

from src.mcp.config import DECAY

logger = logging.getLogger(__name__)

SECONDS_PER_DAY = 86400


def decay_score(last_accessed: float, now: float = None) -> float:
    """
    Calculate the temporal decay multiplier for a chunk.
    
    Args:
        last_accessed: Unix timestamp of last access.
        now: Current time (default: time.time()).
    
    Returns:
        Decay multiplier between 0 and 1.
    """
    now = now or time.time()
    days = max(0, (now - last_accessed) / SECONDS_PER_DAY)
    return math.exp(-DECAY.lambda_decay * days)


def apply_temporal_ranking(results: list[dict], now: float = None) -> list[dict]:
    """
    Re-rank retrieval results by applying temporal decay to their similarity scores.
    
    Each result dict must have:
        - 'distance': cosine distance from ChromaDB (lower = more similar)
        - 'metadata.last_accessed': Unix timestamp
    
    Adds 'temporal_score' and 'decay_factor' to each result.
    Returns results sorted by temporal_score (highest first).
    """
    now = now or time.time()
    
    for result in results:
        # ChromaDB returns distance (0 = identical, 2 = opposite for cosine)
        # Convert to similarity: similarity = 1 - distance
        distance = result.get("distance", 0)
        similarity = max(0, 1 - distance)
        
        last_accessed = result.get("metadata", {}).get("last_accessed", now)
        decay = decay_score(last_accessed, now)
        
        result["similarity"] = round(similarity, 4)
        result["decay_factor"] = round(decay, 4)
        result["temporal_score"] = round(similarity * decay, 4)
    
    # Sort by temporal_score descending (highest = most relevant + recent)
    results.sort(key=lambda r: r["temporal_score"], reverse=True)
    
    logger.debug(
        f"Temporal ranking applied to {len(results)} results. "
        f"Top score: {results[0]['temporal_score'] if results else 'N/A'}"
    )
    return results
