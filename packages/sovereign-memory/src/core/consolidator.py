"""
Memory Consolidator

Generates weekly digests from WARM-tier chunks, stores them in COLD tier.
Uses the Synthesizer (Qwen3) to produce concise summaries that preserve
key decisions, entities, and rationale.

This implements the hierarchical summarization pattern:
Raw chunks → Session clusters → Weekly digest → Archival
"""

import time
import logging
from collections import defaultdict

from src.core.synthesizer import Synthesizer
from src.core import embedder
from src.core import extractor
from src.stores.chroma_store import ChromaStore
from src.stores.graph_store import GraphStore
from src.mcp.config import TIER

logger = logging.getLogger(__name__)

SECONDS_PER_DAY = 86400


class Consolidator:
    """
    Periodically consolidates WARM-tier memory into COLD-tier digests.
    
    Process:
    1. Gather all WARM chunks older than warm_max_age_days
    2. Group by source/topic
    3. Ask Synthesizer to generate a digest per group
    4. Embed and store digest in COLD tier
    5. Extract entities from digest → update graph
    6. Delete original WARM chunks
    """

    def __init__(
        self,
        chroma: ChromaStore,
        graph: GraphStore,
        synthesizer: Synthesizer,
    ):
        self.chroma = chroma
        self.graph = graph
        self.synthesizer = synthesizer

    def consolidate(self, time_period: str = "recent period") -> dict:
        """
        Run a full consolidation cycle.
        
        Args:
            time_period: Human-readable label for the digest.
        
        Returns:
            Summary of consolidation actions.
        """
        now = time.time()
        cutoff = now - (TIER.warm_max_age_days * SECONDS_PER_DAY)
        
        # Step 1: Gather qualifying WARM chunks
        warm_items = self.chroma.warm.get(include=["documents", "metadatas"])
        candidates = []
        
        for i, chunk_id in enumerate(warm_items["ids"]):
            meta = warm_items["metadatas"][i]
            last_accessed = meta.get("last_accessed", meta.get("created_at", now))
            if last_accessed < cutoff:
                candidates.append({
                    "id": chunk_id,
                    "content": warm_items["documents"][i],
                    "metadata": meta,
                })
        
        if not candidates:
            logger.info("No WARM chunks qualify for consolidation.")
            return {"digests_created": 0, "chunks_consolidated": 0}
        
        logger.info(f"Found {len(candidates)} WARM chunks for consolidation.")
        
        # Step 2: Group by source
        groups = defaultdict(list)
        for chunk in candidates:
            source = chunk["metadata"].get("source", "unknown")
            groups[source].append(chunk)
        
        # Step 3: Generate digest per group
        digests_created = 0
        chunks_consolidated = 0
        
        for source, chunks in groups.items():
            try:
                digest_text = self.synthesizer.generate_digest(
                    chunks=chunks,
                    time_period=time_period,
                )
                
                if not digest_text or digest_text.startswith("[Synthesis"):
                    logger.warning(f"Digest generation failed for source={source}")
                    continue
                
                # Step 4: Embed and store digest in COLD
                digest_embedding = embedder.embed_text(digest_text)
                digest_id = self.chroma.add(
                    content=digest_text,
                    embedding=digest_embedding,
                    source=f"digest:{source}",
                    tags=["digest", "consolidation"],
                    tier="cold",
                )
                
                # Step 5: Extract entities from digest → update graph
                extraction = extractor.extract_entities(digest_text)
                for entity in extraction.entities:
                    self.graph.upsert_entity(
                        name=entity.text,
                        entity_type=entity.label,
                        chunk_id=digest_id,
                        source=f"digest:{source}",
                    )
                for rel in extraction.relationships:
                    self.graph.create_relationship(**rel)
                
                # Step 6: Delete original WARM chunks
                for chunk in chunks:
                    self.chroma.delete(chunk["id"], tier="warm")
                    self.graph.delete_entities_for_chunk(chunk["id"])
                
                digests_created += 1
                chunks_consolidated += len(chunks)
                
                logger.info(
                    f"Consolidated {len(chunks)} chunks from '{source}' "
                    f"into digest {digest_id[:8]}..."
                )
                
            except Exception as e:
                logger.error(f"Consolidation failed for source={source}: {e}")
                continue
        
        summary = {
            "digests_created": digests_created,
            "chunks_consolidated": chunks_consolidated,
            "sources_processed": list(groups.keys()),
        }
        logger.info(f"Consolidation complete: {summary}")
        return summary
