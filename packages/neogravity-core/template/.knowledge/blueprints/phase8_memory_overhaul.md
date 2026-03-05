# Part B: Hybrid-RAG → Local MoE MCP Server — Refined Plan v4

*Based on reading every line of the existing codebase. This plan maps reality, not assumptions.*

---

## Critical Discovery
> **The entity extraction was never built.** `ingestion_service.py` L42-71 is a placeholder that splits on uppercase words. GLiNER replaces a fake with a real zero-hallucination extractor.

## Codebase Assessment

| File | Lines | Verdict | Action |
|------|-------|---------|--------|
| `orchestration_service.py` | 29 | 🟢 REUSE | MoE router follows same pattern |
| `ingestion_service.py` | 158 | 🟡 REWRITE | Chunking reusable, entity extraction was placeholder |
| `retrieval_service.py` | 203 | 🟡 REWRITE | Hybrid search pattern reusable, swap Gemini→Qwen3 |
| `embedding_service.py` | 57 | 🔴 REPLACE | Gemini API → sentence-transformers |
| `intent_classifier.py` | 46 | 🟢 REUSE | Clean keyword routing, no deps |
| `neo4j_db.py` | 90 | 🟢 REUSE 80% | Change URI from AuraDB → local CE |
| `neon_db.py` | 60 | 🔴 DELETE | Full swap to ChromaDB |
| `main.py` | 83 | 🔴 DELETE | FastAPI → MCP stdio |

## Build Order (Bottom-Up, Dependency-Safe)

### Layer 0: Foundation
- `config.py`, `requirements.txt`, `docker-compose.yml`, `.env.example`, project structure
- Archive old code to `archived/`

### Layer 1: Stores
- `chroma_store.py` (3-collection: HOT, WARM, COLD)
- `graph_store.py` (adapt neo4j_db.py → local CE)

### Layer 2: Core Specialists
- `embedder.py` (all-MiniLM-L6-v2, 90MB, CPU)
- `extractor.py` (GLiNER, ~200MB, CPU)
- `synthesizer.py` (Qwen3-30B-A3B via Ollama, on-demand)

### Layer 3: Intelligence
- `chunker.py`, `router.py`, `tiers.py`, `temporal.py`, `surprise.py`, `consolidator.py`

### Layer 4: MCP Server
- `server.py` — 5 tools via stdio transport

### Layer 5: Scripts + Docs + Integration
- CLI tools, README, architecture docs, Antigravity wiring

## Key Changes from v3
- `src/` package layout (proper Python packaging)
- Bottom-up build order (prevents circular imports)
- `archived/` for old cloud code (preserves reference)
- Entity extraction identified as placeholder → GLiNER is critical path
