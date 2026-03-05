"""
ChromaDB 3-Tier Vector Store

Manages three ChromaDB collections (HOT, WARM, COLD) for temporal memory storage.
Each chunk is stored with metadata for tier management, temporal decay, and surprise detection.
"""

import time
import hashlib
import logging
from typing import Optional
from dataclasses import dataclass, field

import chromadb
from chromadb.config import Settings

from src.mcp.config import STORES, TIER

logger = logging.getLogger(__name__)


@dataclass
class MemoryChunk:
    """A single memory chunk with metadata for tier management."""
    id: str
    content: str
    embedding: list[float]
    source: str
    tier: str                    # "hot", "warm", "cold"
    created_at: float            # Unix timestamp
    last_accessed: float         # Unix timestamp
    access_count: int = 0
    tags: list[str] = field(default_factory=list)
    surprise_flag: bool = False
    surprise_conflicting_id: Optional[str] = None


class ChromaStore:
    """
    3-collection ChromaDB manager for temporal memory tiers.
    
    Collections:
        - memory_hot:  Working memory (< 7 days, frequently accessed)
        - memory_warm: Short-term reference (7-30 days)
        - memory_cold: Archival / consolidated digests (> 30 days)
    """

    def __init__(self, persist_path: str = None):
        persist_path = persist_path or STORES.chroma_persist_path
        self.client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize 3 tier collections
        self.hot = self.client.get_or_create_collection(
            name=STORES.chroma_collection_hot,
            metadata={"hnsw:space": "cosine"}
        )
        self.warm = self.client.get_or_create_collection(
            name=STORES.chroma_collection_warm,
            metadata={"hnsw:space": "cosine"}
        )
        self.cold = self.client.get_or_create_collection(
            name=STORES.chroma_collection_cold,
            metadata={"hnsw:space": "cosine"}
        )
        
        self._collections = {
            "hot": self.hot,
            "warm": self.warm,
            "cold": self.cold,
        }
        
        logger.info(
            f"ChromaStore initialized. HOT={self.hot.count()}, "
            f"WARM={self.warm.count()}, COLD={self.cold.count()}"
        )

    def _collection_for(self, tier: str):
        """Get the ChromaDB collection for a given tier name."""
        coll = self._collections.get(tier)
        if coll is None:
            raise ValueError(f"Unknown tier: {tier}. Must be 'hot', 'warm', or 'cold'.")
        return coll

    def add(
        self,
        content: str,
        embedding: list[float],
        source: str,
        tags: list[str] = None,
        tier: str = "hot",
        chunk_id: str = None,
        intent: str = "general",
    ) -> str:
        """
        Add a memory chunk to the specified tier.
        
        Uses SHA-256 content hash as chunk ID for idempotent ingestion.
        Calling upsert() with the same content updates metadata instead
        of creating duplicates.
        
        Returns the chunk ID.
        """
        # Dedup: content hash as ID — same content always gets same ID
        chunk_id = chunk_id or hashlib.sha256(content.encode()).hexdigest()[:16]
        now = time.time()
        
        metadata = {
            "source": source,
            "intent": intent,
            "tier": tier,
            "created_at": now,
            "last_accessed": now,
            "access_count": 1,
            "tags": ",".join(tags or []),
            "surprise_flag": False,
            "surprise_conflicting_id": "",
        }
        
        collection = self._collection_for(tier)
        # upsert() is idempotent — updates if ID exists, adds if not
        collection.upsert(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
        )
        
        logger.info(f"Upserted chunk {chunk_id[:8]}... to {tier} tier (source={source}, intent={intent})")
        return chunk_id

    def query(
        self,
        query_embedding: list[float],
        tier: str = None,
        top_k: int = 5,
        where: dict = None,
    ) -> list[dict]:
        """
        Query for similar chunks. If tier is None, searches HOT then WARM.
        
        Returns list of dicts with keys: id, content, metadata, distance.
        """
        tiers_to_search = [tier] if tier else ["hot", "warm"]
        results = []
        
        for t in tiers_to_search:
            collection = self._collection_for(t)
            if collection.count() == 0:
                continue
                
            query_result = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, collection.count()),
                where=where,
                include=["documents", "metadatas", "distances"],
            )
            
            for i in range(len(query_result["ids"][0])):
                chunk_id = query_result["ids"][0][i]
                results.append({
                    "id": chunk_id,
                    "content": query_result["documents"][0][i],
                    "metadata": query_result["metadatas"][0][i],
                    "distance": query_result["distances"][0][i],
                    "tier": t,
                })
                
                # Update access metadata
                self._touch(chunk_id, t)
        
        # Sort by distance (lower = more similar for cosine)
        results.sort(key=lambda x: x["distance"])
        return results[:top_k]

    def _touch(self, chunk_id: str, tier: str):
        """Update last_accessed timestamp and increment access_count."""
        collection = self._collection_for(tier)
        try:
            existing = collection.get(ids=[chunk_id], include=["metadatas"])
            if existing["metadatas"]:
                meta = existing["metadatas"][0]
                meta["last_accessed"] = time.time()
                meta["access_count"] = meta.get("access_count", 0) + 1
                collection.update(ids=[chunk_id], metadatas=[meta])
        except Exception as e:
            logger.warning(f"Failed to touch chunk {chunk_id}: {e}")

    def get_recent(self, n: int = 10, tier: str = "hot") -> list[dict]:
        """Get the N most recently added chunks from a tier."""
        collection = self._collection_for(tier)
        count = collection.count()
        if count == 0:
            return []
        
        # ChromaDB doesn't support ORDER BY, so fetch all and sort
        all_items = collection.get(
            include=["documents", "metadatas"],
            limit=min(n * 3, count),  # Overfetch to allow sorting
        )
        
        items = []
        for i in range(len(all_items["ids"])):
            items.append({
                "id": all_items["ids"][i],
                "content": all_items["documents"][i],
                "metadata": all_items["metadatas"][i],
                "tier": tier,
            })
        
        items.sort(key=lambda x: x["metadata"].get("created_at", 0), reverse=True)
        return items[:n]

    def move_chunk(self, chunk_id: str, from_tier: str, to_tier: str):
        """Move a chunk between tiers (promotion/demotion)."""
        source_coll = self._collection_for(from_tier)
        target_coll = self._collection_for(to_tier)
        
        # Get the chunk data from source
        chunk_data = source_coll.get(
            ids=[chunk_id],
            include=["documents", "embeddings", "metadatas"],
        )
        
        if not chunk_data["ids"]:
            logger.warning(f"Chunk {chunk_id} not found in {from_tier}")
            return
        
        # Update tier metadata
        metadata = chunk_data["metadatas"][0]
        metadata["tier"] = to_tier
        
        # Add to target
        target_coll.add(
            ids=[chunk_id],
            documents=[chunk_data["documents"][0]],
            embeddings=[chunk_data["embeddings"][0]],
            metadatas=[metadata],
        )
        
        # Remove from source
        source_coll.delete(ids=[chunk_id])
        
        logger.info(f"Moved chunk {chunk_id[:8]}... from {from_tier} → {to_tier}")

    def delete(self, chunk_id: str, tier: str = None):
        """Delete a chunk by ID. If tier is None, searches all tiers."""
        tiers_to_check = [tier] if tier else ["hot", "warm", "cold"]
        for t in tiers_to_check:
            collection = self._collection_for(t)
            try:
                collection.delete(ids=[chunk_id])
                logger.info(f"Deleted chunk {chunk_id[:8]}... from {t}")
                return True
            except Exception:
                continue
        return False

    def flag_surprise(self, chunk_id: str, tier: str, conflicting_id: str):
        """Mark a chunk as having a surprise/contradiction."""
        collection = self._collection_for(tier)
        existing = collection.get(ids=[chunk_id], include=["metadatas"])
        if existing["metadatas"]:
            meta = existing["metadatas"][0]
            meta["surprise_flag"] = True
            meta["surprise_conflicting_id"] = conflicting_id
            collection.update(ids=[chunk_id], metadatas=[meta])
            logger.info(f"Flagged surprise on chunk {chunk_id[:8]}... (conflicts with {conflicting_id[:8]}...)")

    def get_tier_stats(self) -> dict:
        """Get counts for each tier."""
        return {
            "hot": self.hot.count(),
            "warm": self.warm.count(),
            "cold": self.cold.count(),
            "total": self.hot.count() + self.warm.count() + self.cold.count(),
        }
