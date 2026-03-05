"""
3-Tier Memory Manager

Handles automatic promotion (WARM→HOT) and demotion (HOT→WARM, WARM→COLD)
based on access patterns and temporal thresholds.

Inspired by MCP TITAN's 3-tier architecture but uses exponential temporal
decay instead of momentum-based learning.
"""

import time
import logging

from src.mcp.config import TIER
from src.stores.chroma_store import ChromaStore

logger = logging.getLogger(__name__)

SECONDS_PER_DAY = 86400


class TierManager:
    """
    Manages chunk lifecycle across HOT, WARM, and COLD tiers.
    
    Promotion: WARM → HOT when access_count >= hot_min_access_count within window
    Demotion:  HOT → WARM when no access for hot_max_age_days
               WARM → COLD when no access for warm_max_age_days
    """

    def __init__(self, chroma: ChromaStore):
        self.chroma = chroma

    def run_maintenance(self) -> dict:
        """
        Run a full tier maintenance cycle.
        
        Scans all tiers and moves chunks based on access patterns.
        Should be called periodically (e.g., at session start/end).
        
        Returns a summary of actions taken.
        """
        now = time.time()
        actions = {"promoted": 0, "demoted_to_warm": 0, "demoted_to_cold": 0}

        # Phase 1: Demote stale HOT → WARM
        hot_items = self.chroma.hot.get(include=["metadatas"])
        for i, chunk_id in enumerate(hot_items["ids"]):
            meta = hot_items["metadatas"][i]
            last_accessed = meta.get("last_accessed", meta.get("created_at", now))
            age_days = (now - last_accessed) / SECONDS_PER_DAY
            
            if age_days > TIER.hot_max_age_days:
                self.chroma.move_chunk(chunk_id, "hot", "warm")
                actions["demoted_to_warm"] += 1

        # Phase 2: Promote frequently-accessed WARM → HOT
        warm_items = self.chroma.warm.get(include=["metadatas"])
        for i, chunk_id in enumerate(warm_items["ids"]):
            meta = warm_items["metadatas"][i]
            access_count = meta.get("access_count", 0)
            last_accessed = meta.get("last_accessed", 0)
            recency_days = (now - last_accessed) / SECONDS_PER_DAY
            
            # Promote if accessed frequently AND recently
            if (access_count >= TIER.hot_min_access_count 
                    and recency_days <= TIER.hot_max_age_days):
                self.chroma.move_chunk(chunk_id, "warm", "hot")
                actions["promoted"] += 1

        # Phase 3: Demote stale WARM → COLD
        # Re-fetch after potential promotions
        warm_items = self.chroma.warm.get(include=["metadatas"])
        for i, chunk_id in enumerate(warm_items["ids"]):
            meta = warm_items["metadatas"][i]
            last_accessed = meta.get("last_accessed", meta.get("created_at", now))
            age_days = (now - last_accessed) / SECONDS_PER_DAY
            
            if age_days > TIER.warm_max_age_days:
                self.chroma.move_chunk(chunk_id, "warm", "cold")
                actions["demoted_to_cold"] += 1

        logger.info(
            f"Tier maintenance: {actions['promoted']} promoted, "
            f"{actions['demoted_to_warm']} HOT→WARM, "
            f"{actions['demoted_to_cold']} WARM→COLD"
        )
        return actions

    def get_chunk_tier_info(self, chunk_id: str) -> dict | None:
        """Get current tier and metadata for a chunk."""
        for tier_name in ["hot", "warm", "cold"]:
            collection = self.chroma._collection_for(tier_name)
            result = collection.get(ids=[chunk_id], include=["metadatas"])
            if result["ids"]:
                meta = result["metadatas"][0]
                last_accessed = meta.get("last_accessed", 0)
                age_days = (time.time() - last_accessed) / SECONDS_PER_DAY
                return {
                    "chunk_id": chunk_id,
                    "tier": tier_name,
                    "access_count": meta.get("access_count", 0),
                    "age_days": round(age_days, 1),
                    "surprise_flag": meta.get("surprise_flag", False),
                }
        return None
