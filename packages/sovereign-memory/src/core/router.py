"""
MoE Operation Router

Routes memory operations to the appropriate specialist(s).
Adapted from the original intent_classifier.py — same pattern,
expanded for the full MCP tool repertoire.

This is the outer MoE router. It decides WHICH specialists to invoke
for each operation. The specialists themselves handle the actual work.
"""

import logging
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class Operation(Enum):
    """Memory operations that the MCP server exposes."""
    INGEST = "ingest"           # Chunk → Embed → Extract → Store
    QUERY = "query"             # Embed → Search → (optional Synthesize)
    RECENT = "recent"           # Direct ChromaDB lookup (no models needed)
    FORGET = "forget"           # Direct delete (no models needed)
    CONSOLIDATE = "consolidate" # Retrieve WARM → Synthesize digest → Store COLD


@dataclass
class RoutingPlan:
    """
    Which specialists to activate for this operation.
    True = load/use this specialist. False = skip.
    """
    operation: Operation
    use_embedder: bool = False      # Specialist 1: MiniLM
    use_extractor: bool = False     # Specialist 2: GLiNER
    use_synthesizer: bool = False   # Specialist 3: Qwen3
    use_chroma: bool = False        # Vector store
    use_neo4j: bool = False         # Graph store
    synthesize_answer: bool = False # Whether to generate a full answer vs return raw chunks


# Pre-computed routing table — zero runtime cost
_ROUTING_TABLE: dict[Operation, RoutingPlan] = {
    Operation.INGEST: RoutingPlan(
        operation=Operation.INGEST,
        use_embedder=True,      # Embed chunks for vector storage
        use_extractor=True,     # Extract entities for graph storage
        use_synthesizer=False,  # No synthesis during ingestion
        use_chroma=True,        # Store embeddings
        use_neo4j=True,         # Store entity graph
    ),
    Operation.QUERY: RoutingPlan(
        operation=Operation.QUERY,
        use_embedder=True,      # Embed query for vector search
        use_extractor=False,    # No extraction during query
        use_synthesizer=True,   # Synthesize answer from results
        use_chroma=True,        # Vector search
        use_neo4j=True,         # Graph augmentation
        synthesize_answer=True,
    ),
    Operation.RECENT: RoutingPlan(
        operation=Operation.RECENT,
        use_embedder=False,     # No embedding needed
        use_extractor=False,    # No extraction needed
        use_synthesizer=False,  # Just return raw results
        use_chroma=True,        # Direct lookup
        use_neo4j=False,        # No graph needed
    ),
    Operation.FORGET: RoutingPlan(
        operation=Operation.FORGET,
        use_embedder=False,
        use_extractor=False,
        use_synthesizer=False,
        use_chroma=True,        # Delete from vector store
        use_neo4j=True,         # Cascade delete from graph
    ),
    Operation.CONSOLIDATE: RoutingPlan(
        operation=Operation.CONSOLIDATE,
        use_embedder=True,      # Embed the generated digest
        use_extractor=True,     # Extract entities from digest
        use_synthesizer=True,   # Generate the digest itself
        use_chroma=True,        # Read WARM, write COLD
        use_neo4j=True,         # Update entity graph
    ),
}


def route(operation: Operation) -> RoutingPlan:
    """
    Get the routing plan for an operation.
    
    This is a zero-cost lookup — the routing table is pre-computed at module load.
    No ML model is used for routing here (unlike the Sentinel's SPE router),
    because our operation space is small and deterministic.
    """
    plan = _ROUTING_TABLE.get(operation)
    if plan is None:
        raise ValueError(f"Unknown operation: {operation}")
    
    logger.debug(
        f"Routed {operation.value}: "
        f"embed={plan.use_embedder}, extract={plan.use_extractor}, "
        f"synth={plan.use_synthesizer}, chroma={plan.use_chroma}, "
        f"neo4j={plan.use_neo4j}"
    )
    return plan


def classify_query_intent(query: str) -> Operation:
    """
    Classify a natural language query into an operation.
    Adapted from intent_classifier.py — keyword-based, zero overhead.
    
    Used by the MCP server when it receives a freeform request.
    """
    lower = query.lower().strip()
    
    # Ingest signals
    if any(kw in lower for kw in ["ingest", "add", "store", "save", "upload", "push"]):
        return Operation.INGEST
    
    # Forget signals
    if any(kw in lower for kw in ["forget", "delete", "remove", "clear", "prune"]):
        return Operation.FORGET
    
    # Recent signals
    if any(kw in lower for kw in ["recent", "latest", "last", "newest"]):
        return Operation.RECENT
    
    # Consolidate signals
    if any(kw in lower for kw in ["consolidate", "digest", "summarize all", "weekly"]):
        return Operation.CONSOLIDATE
    
    # Default: query/retrieval
    return Operation.QUERY
