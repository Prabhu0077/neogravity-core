# Sovereign Memory — 2026 Research Findings & Improvement Roadmap

_Research conducted: 2026-03-04_

---

## Executive Summary

Our Sovereign Memory MoE architecture is **architecturally sound** — the 3-specialist design, 3-tier temporal storage, and MCP stdio transport align with current 2026 best practices. However, **3 component-level upgrades** and **2 architectural additions** can bring it from "working prototype" to "production-grade."

---

## Finding 1: GLiNER2 Replaces GLiNER v1

> **Impact: HIGH | Effort: LOW (pip swap)**

### What Changed (July 2025 → Feb 2026)

- **GLiNER2** unifies NER + Text Classification + Structured Data Extraction into ONE model via schema-based interface
- **GLiNER-bi-Encoder** achieves **130x throughput** when handling 1024+ entity types (constant memory regardless of type count)
- Matches **GPT-4o F1 score on CrossNER**, surpasses in AI/Literature domains
- Still CPU-first, under 500M params

### Current State (Ours)

We use `gliner` (v1) with `urchade/gliner_medium-v2.1` — single-task NER only.

### Recommended Upgrade

```diff
# requirements.txt
-gliner>=0.2
+gliner2>=0.1
```

```python
# extractor.py — schema-based interface
schema = {
    "entities": ["person", "organization", "technology", "product", "location"],
    "relations": True,  # built-in relationship extraction!
    "classification": {"relevant", "noise"}  # text-level classification
}
```

**Benefit:** Eliminate our manual `_infer_relationships()` heuristic. GLiNER2 does NER + RE + classification in one forward pass.

---

## Finding 2: Qwen3.5 Supersedes Qwen3

> **Impact: MEDIUM | Effort: LOW (model swap)**

### What Changed (Feb-Mar 2026)

- **Qwen3.5** uses **Gated Delta Networks (GDN) + sparse MoE** hybrid architecture
- **9B variant** available — sweet spot for edge devices
- Reduced hallucinations via reinforced logical consistency
- **76.5 on IFBench** (instruction following) — surpasses GPT-5.2
- Native multimodal (we don't need this now, but future-proofing)

### Current State (Ours)

We use `qwen3:8b` — good, but superseded.

### Recommended Upgrade (when available on Ollama)

```bash
ollama pull qwen3.5:9b
# or the MoE variant when released
ollama pull qwen3.5:35b-a3b  # only 3B active, similar RAM to current
```

**Status:** Check `ollama list` periodically. Qwen3.5 models are landing on Ollama now.

---

## Finding 3: Better Embedding Model Alternatives

> **Impact: MEDIUM | Effort: LOW (config change)**

### What Changed

`all-MiniLM-L6-v2` is still fast but accuracy-wise outclassed by:

| Model                    | Params    | Advantage                                      | CPU Speed       |
| ------------------------ | --------- | ---------------------------------------------- | --------------- |
| **Nomic Embed v2**       | MoE-based | Higher accuracy, multilingual                  | Comparable      |
| **BGE-M3**               | ~300M     | 8192 token context, compression-friendly       | Slightly slower |
| **Qwen3-Embedding-0.6B** | 600M      | Flexible vector dimensions, instruction-aware  | Comparable      |
| **E5-small**             | ~100M     | 100% Top-5 accuracy in retrieval, 16ms latency | _Faster_        |

### Recommended Next Step

Keep MiniLM for now (it's working, fast). When we have time:

1. Benchmark E5-small vs MiniLM on our actual `.knowledge/` corpus
2. If accuracy improves by >5%, swap. Our config already supports `EMBEDDING_MODEL` env var — true hot-swap.

---

## Finding 4: MCP Tool Design Best Practices

> **Impact: HIGH | Effort: MEDIUM**

### Key 2026 Findings

1. **Design tools around user intents, not API calls** — our 5 tools (ingest/query/recent/forget/consolidate) already follow this pattern ✅
2. **Flatten arguments to prevent hallucinations** — we use simple string args ✅
3. **Use stderr for all logging** (stdout = protocol wire) — we do this ✅
4. **STDIO ~10MB footprint** vs 50MB for HTTP — we chose correctly ✅
5. **⚠️ MISSING: Context compaction** — production systems need summarization of older context before sending to LLM
6. **⚠️ MISSING: "Just-in-time" retrieval** — the `memory_query` tool should support intent-aware pre-filtering

### Recommended Additions

**New Tool: `memory_health`** — Returns tier stats, model load status, Neo4j connectivity, RAM usage. Critical for observability.

**New Tool: `memory_context`** — Returns a pre-compiled context block (recent + relevant) sized to fit within a target token budget. This is the "context compaction" pattern recommended in all 2026 literature.

---

## Finding 5: GraphRAG Production Patterns

> **Impact: MEDIUM | Effort: MEDIUM**

### Key 2026 Findings

- Neo4j 5.18+ has **native vector search** — could eliminate the need for a separate ChromaDB
- Microsoft GraphRAG is "production-ready" as of August 2025
- Graph databases predicted to become **core AI infrastructure by 2026**
- Multi-level caching is essential for GraphRAG query performance

### Our Position

We already have the right architecture (ChromaDB for vectors + Neo4j for graph). Keep both — ChromaDB is simpler for pure vector ops, Neo4j adds the relationship layer.

### Recommended Addition

Add a **GraphRAG query mode** to `memory_query`:

- When entities are detected in the query, do a graph neighborhood traversal THEN vector search on the connected chunks
- This is the hybrid pattern recommended by both Neo4j and Qdrant teams

---

## Priority Matrix (Updated 2026-03-05 after benchmarking)

| Improvement                         | Impact       | Effort       | Priority                      | Status                                                                  |
| ----------------------------------- | ------------ | ------------ | ----------------------------- | ----------------------------------------------------------------------- |
| **Remove Qwen3:8b from query path** | HIGH         | LOW          | **P0**                        | ✅ DONE — query latency 60s→<1s                                         |
| Add `memory_health` tool            | HIGH         | LOW          | **P0 — Next session**         | Pending                                                                 |
| Add `memory_context` tool           | HIGH         | MEDIUM       | **P1 — This week**            | Pending                                                                 |
| GLiNER → GLiNER2                    | ~~HIGH~~ LOW | ~~LOW~~ HIGH | ~~P0~~ **P3**                 | **REJECTED** — GLiNER2-large=1.95GB (10x current), GLiNER v1 works well |
| Qwen3 → Qwen3.5                     | MEDIUM       | LOW          | **P1 — When on Ollama**       | Pending (consolidation path only)                                       |
| GraphRAG query mode                 | MEDIUM       | MEDIUM       | **P2 — After core is stable** | Pending                                                                 |
| Embedding model benchmark           | MEDIUM       | LOW          | **P2**                        | ✅ DONE — MiniLM wins on our corpus (0.46 discrim vs E5=0.11, BGE=0.27) |

---

## Benchmark Results (2026-03-05, 43GB RAM, Intel CPU, CPU-only)

### Embedding Models

| Model                   | Params | Query Speed | Top-1    | Discrimination |
| ----------------------- | ------ | ----------- | -------- | -------------- |
| **all-MiniLM-L6-v2** ✅ | 22M    | **8.9ms**   | **100%** | **0.4615**     |
| intfloat/e5-small-v2    | 118M   | 19.4ms      | 100%     | 0.1125         |
| BAAI/bge-small-en-v1.5  | 33M    | 18.6ms      | 100%     | 0.2670         |

### Entity Extractors

| Model                   | Size       | Speed       | Result                           |
| ----------------------- | ---------- | ----------- | -------------------------------- |
| **GLiNER v1 medium** ✅ | ~200MB     | ~210ms/text | 4 entities/text, right-sized     |
| GLiNER2-large           | **1.95GB** | N/A         | 10x too large for marginal gains |

### Synthesizer

| Model    | Speed      | RAM   | Decision                                                    |
| -------- | ---------- | ----- | ----------------------------------------------------------- |
| Qwen3:8b | 3.58 tok/s | 5.9GB | **Removed from query path**, kept for offline consolidation |

---

## What We Got RIGHT

| Decision                                | 2026 Research Validates                                          |
| --------------------------------------- | ---------------------------------------------------------------- |
| 3-tier temporal storage (HOT/WARM/COLD) | ✅ Best practice — mirrors working/episodic/long-term memory     |
| MoE over monolithic                     | ✅ MoE is the dominant 2026 pattern for efficiency               |
| STDIO transport                         | ✅ Lower memory footprint, simpler, process-bound lifecycle      |
| Neo4j optional (graceful degradation)   | ✅ Recommended for resilience                                    |
| GLiNER for zero-hallucination NER       | ✅ Confirmed — outperforms LLM extraction                        |
| Temporal decay scoring                  | ✅ Aligns with "selective context injection" best practice       |
| Surprise detection before storage       | ✅ No equivalent found in literature — we're ahead here          |
| **all-MiniLM-L6-v2 for embeddings**     | ✅ **Benchmarked — beats E5 and BGE on our domain corpus**       |
| **No LLM on retrieval path**            | ✅ **Pure retrieval + external LLM synthesis = optimal pattern** |
