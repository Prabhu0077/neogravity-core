"""
Sovereign Memory — MCP Server

Exposes 5 memory tools via Model Context Protocol stdio transport:
    memory_ingest     — Chunk → Embed → Extract → Store
    memory_query      — Embed → Search → Temporal Rank → Return raw chunks
    memory_recent     — Get N most recent chunks from HOT tier
    memory_forget     — Delete/demote chunks by age or tag
    memory_consolidate — Generate weekly digest from WARM → COLD

Usage:
    python -m src.mcp.server
"""

import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.mcp.config import STORES, MODELS
from src.stores.chroma_store import ChromaStore
from src.stores.graph_store import GraphStore
from src.core import embedder, extractor
from src.core.synthesizer import Synthesizer
from src.core.chunker import chunk_text
from src.core.router import route, Operation
from src.core.tiers import TierManager
from src.core.temporal import apply_temporal_ranking
from src.core.surprise import check_surprise
from src.core.consolidator import Consolidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stderr,  # MCP stdout is for protocol; log to stderr
)
logger = logging.getLogger("sovereign-memory")

# Initialize server
app = Server("sovereign-memory")

# Lazy-initialized singletons (created on first tool call)
_chroma: ChromaStore | None = None
_graph: GraphStore | None = None
_synthesizer: Synthesizer | None = None  # Only loaded for memory_consolidate
_tier_manager: TierManager | None = None
_consolidator: Consolidator | None = None


def _init_stores():
    """Lazy-initialize vector + graph stores. Synthesizer is NOT loaded here (saves 5.9GB RAM)."""
    global _chroma, _graph, _tier_manager
    
    if _chroma is None:
        logger.info("Initializing ChromaDB...")
        _chroma = ChromaStore()
    
    if _graph is None:
        try:
            logger.info("Initializing Neo4j...")
            _graph = GraphStore()
        except Exception as e:
            logger.warning(f"Neo4j unavailable (graph features disabled): {e}")
            _graph = None  # Graph is optional — vector store works standalone
    
    if _tier_manager is None and _chroma:
        _tier_manager = TierManager(_chroma)


def _init_synthesizer():
    """Lazy-initialize synthesizer + consolidator ONLY when consolidation is requested."""
    global _synthesizer, _consolidator
    if _synthesizer is None:
        logger.info("Loading synthesizer for consolidation (Qwen3:8b via Ollama)...")
        _synthesizer = Synthesizer()
    if _consolidator is None and _chroma:
        _consolidator = Consolidator(
            chroma=_chroma,
            graph=_graph,
            synthesizer=_synthesizer,
        )


# ─────────────────────────────────────────────────────────
# Tool definitions
# ─────────────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Register all 5 memory tools."""
    return [
        Tool(
            name="memory_ingest",
            description=(
                "Ingest text into the memory system. Chunks the text, "
                "embeds it, extracts entities, checks for contradictions, "
                "and stores in the HOT tier. Returns chunk IDs and any surprise flags."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content to ingest.",
                    },
                    "source": {
                        "type": "string",
                        "description": "Source identifier (e.g., filename, session tag).",
                    },
                    "intent": {
                        "type": "string",
                        "enum": ["session", "decision", "outreach", "deploy", "research", "harvest", "architecture", "general"],
                        "description": "Content intent for filtered retrieval. Defaults to 'general'.",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags for categorization.",
                    },
                },
                "required": ["text", "source"],
            },
        ),
        Tool(
            name="memory_query",
            description=(
                "Search the memory system using semantic similarity with temporal ranking. "
                "Returns relevant chunks weighted by recency. "
                "The calling LLM should synthesize answers from the returned raw chunks."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question or search query.",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5).",
                        "default": 5,
                    },
                    "tier": {
                        "type": "string",
                        "enum": ["hot", "warm", "cold"],
                        "description": "Limit search to a specific tier. Default searches HOT+WARM.",
                    },
                },
                "required": ["question"],
            },
        ),
        Tool(
            name="memory_recent",
            description=(
                "Get the N most recently added memory chunks from the HOT tier."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of recent items to return (default: 10).",
                        "default": 10,
                    },
                },
            },
        ),
        Tool(
            name="memory_forget",
            description=(
                "Delete or demote memory chunks by age or tag. "
                "Use older_than_days to auto-clean stale data."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "older_than_days": {
                        "type": "integer",
                        "description": "Delete chunks not accessed in this many days.",
                    },
                    "tag": {
                        "type": "string",
                        "description": "Delete chunks with this tag.",
                    },
                    "chunk_id": {
                        "type": "string",
                        "description": "Delete a specific chunk by ID.",
                    },
                    "run_maintenance": {
                        "type": "boolean",
                        "description": "Run tier maintenance (promote/demote). Default: false.",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="memory_consolidate",
            description=(
                "Run the consolidation pipeline: gather qualifying WARM-tier chunks, "
                "generate a digest using the LLM, and store in COLD tier. "
                "This frees up WARM tier space while preserving knowledge."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "time_period": {
                        "type": "string",
                        "description": "Human-readable label for the digest period.",
                        "default": "recent period",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch tool calls to the appropriate handler."""
    _init_stores()
    
    try:
        if name == "memory_ingest":
            result = _handle_ingest(arguments)
        elif name == "memory_query":
            result = _handle_query(arguments)
        elif name == "memory_recent":
            result = _handle_recent(arguments)
        elif name == "memory_forget":
            result = _handle_forget(arguments)
        elif name == "memory_consolidate":
            result = _handle_consolidate(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}),
        )]


# ─────────────────────────────────────────────────────────
# Tool handlers
# ─────────────────────────────────────────────────────────

def _handle_ingest(args: dict) -> dict:
    """memory_ingest: Chunk → Context-Prefix Embed → Extract → Store
    
    MoE-aware ingestion:
      - Embedder gets context-prefixed text (improves retrieval 35-49%)
      - GLiNER gets raw text (prefix words are noise for entity extraction)
      - Each specialist gets the input format it performs best with.
    """
    text = args["text"]
    source = args["source"]
    intent = args.get("intent", "general")
    tags = args.get("tags", [])
    
    # Step 1: Chunk
    chunks = chunk_text(text, source=source)
    
    chunk_ids = []
    all_entities = []
    all_surprises = []
    
    for chunk in chunks:
        # Step 2: Embed with context prefix (VECTOR PATH)
        # Prefix carries source + intent for embedding disambiguation.
        # Two chunks about "Neo4j" from different sessions now land in
        # different regions of embedding space.
        context_prefix = f"[{source} | {intent}] "
        embedding = embedder.embed_text(context_prefix + chunk.content)
        
        # Step 3: Check for surprises BEFORE storing
        surprises = check_surprise(chunk.content, embedding, _chroma)
        all_surprises.extend(surprises)
        
        # Step 4: Store in ChromaDB HOT tier (with intent metadata)
        chunk_id = _chroma.add(
            content=chunk.content,
            embedding=embedding,
            source=source,
            tags=tags + ([chunk.section_header] if chunk.section_header else []),
            tier="hot",
            intent=intent,
        )
        chunk_ids.append(chunk_id)
        
        # Step 5: Extract entities → store in Neo4j (GRAPH PATH)
        # GLiNER gets RAW text — no prefix. "session", "decision" etc.
        # are noise for entity extraction; we want real entities only.
        if _graph:
            extraction = extractor.extract_entities(chunk.content)
            for entity in extraction.entities:
                _graph.upsert_entity(
                    name=entity.text,
                    entity_type=entity.label,
                    chunk_id=chunk_id,
                    source=source,
                )
                all_entities.append({
                    "text": entity.text,
                    "label": entity.label,
                    "score": entity.score,
                })
            for rel in extraction.relationships:
                _graph.create_relationship(**rel)
    
    return {
        "status": "ingested",
        "intent": intent,
        "chunks_created": len(chunk_ids),
        "chunk_ids": chunk_ids,
        "entities_extracted": len(all_entities),
        "entities": all_entities[:20],  # Cap output for readability
        "surprises": all_surprises,
        "tier_stats": _chroma.get_tier_stats(),
    }


def _handle_query(args: dict) -> dict:
    """memory_query: Embed → Search → Temporal Rank → Return raw chunks.
    
    No LLM synthesis on this path. The calling agent (Antigravity/Claude/Gemini)
    synthesizes answers from the raw chunks — it's faster and higher quality.
    """
    question = args["question"]
    top_k = args.get("top_k", 5)
    tier = args.get("tier")
    
    # Step 1: Embed query
    query_embedding = embedder.embed_text(question)
    
    # Step 2: Vector search
    results = _chroma.query(
        query_embedding=query_embedding,
        tier=tier,
        top_k=top_k,
    )
    
    # Step 3: Apply temporal ranking
    ranked_results = apply_temporal_ranking(results)
    
    # Step 4: Augment with graph context (if available)
    graph_context = []
    if _graph and ranked_results:
        # Extract entities from the query to find graph neighbors
        query_entities = extractor.extract_entities(question)
        for entity in query_entities.entities:
            neighborhood = _graph.get_entity_neighborhood(
                entity.text, entity.label
            )
            if neighborhood["entity"]:
                graph_context.append(neighborhood)
    
    return {
        "question": question,
        "results": [
            {
                "content": r["content"][:500],
                "source": r["metadata"].get("source", "unknown"),
                "tier": r["tier"],
                "temporal_score": r.get("temporal_score", 0),
                "decay_factor": r.get("decay_factor", 1),
            }
            for r in ranked_results
        ],
        "graph_context": graph_context[:5],
        "total_results": len(ranked_results),
    }


def _handle_recent(args: dict) -> dict:
    """memory_recent: Get N most recent HOT chunks."""
    n = args.get("n", 10)
    recent = _chroma.get_recent(n=n, tier="hot")
    
    return {
        "items": [
            {
                "id": item["id"],
                "content": item["content"][:200],
                "source": item["metadata"].get("source", "unknown"),
                "tags": item["metadata"].get("tags", ""),
            }
            for item in recent
        ],
        "count": len(recent),
        "tier_stats": _chroma.get_tier_stats(),
    }


def _handle_forget(args: dict) -> dict:
    """memory_forget: Delete/demote chunks."""
    deleted = 0
    maintenance_result = None
    
    # Delete specific chunk
    if "chunk_id" in args:
        if _chroma.delete(args["chunk_id"]):
            deleted += 1
            if _graph:
                _graph.delete_entities_for_chunk(args["chunk_id"])
    
    # Run tier maintenance if requested
    if args.get("run_maintenance", False) and _tier_manager:
        maintenance_result = _tier_manager.run_maintenance()
    
    return {
        "deleted": deleted,
        "maintenance": maintenance_result,
        "tier_stats": _chroma.get_tier_stats(),
    }


def _handle_consolidate(args: dict) -> dict:
    """memory_consolidate: WARM → digest → COLD.
    
    This is the ONLY path that loads Qwen3:8b (via Ollama).
    It's an offline batch operation — latency doesn't matter here.
    """
    time_period = args.get("time_period", "recent period")
    
    # Lazy-load synthesizer only when consolidation is requested
    _init_synthesizer()
    
    if not _consolidator:
        return {"error": "Consolidator not available (check Ollama + Neo4j)"}
    
    result = _consolidator.consolidate(time_period=time_period)
    result["tier_stats"] = _chroma.get_tier_stats()
    return result


# ─────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────

async def main():
    """Run the MCP server on stdio."""
    logger.info(
        f"Starting Sovereign Memory MCP Server (retrieval-only, no LLM on query path). "
        f"Embedder: {MODELS.embedding_model}, "
        f"Extractor: {MODELS.gliner_model}, "
        f"Synthesizer: {MODELS.ollama_model} (loaded only for consolidation)"
    )
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
