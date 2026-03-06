# Context Management Research — March 2026

## Problem Statement

Antigravity loses context over 10-15 sessions due to: conversation truncation, Memory MCP graph pollution, lost-in-the-middle effect, growing file surface area, and session boundary amnesia.

## 5 Failure Modes Identified

1. **Conversation Truncation** — already happening. Summaries are lossy compressions of lossy compressions.
2. **Memory MCP Pollution** — 30 entities, 15 stale. 678-line JSON dump wastes attention budget.
3. **Lost-in-the-Middle** — critical mid-session decisions get lowest recall priority.
4. **Growing File Surface** — 50+ files across 6 directories. Can't read everything at boot.
5. **Session Boundary Amnesia** — new conversation = fresh context. BIOS files are single-file summaries.

## Research Approaches Evaluated

### Hierarchical Summarization (Anthropic)

- Multi-level: raw → session → weekly → project
- **Verdict: ADOPTED** — implemented as weekly digests + auto-consolidation

### Vector Database + Semantic Search

- Embed all text, search by meaning instead of keyword
- **Verdict: ADOPTED** — using ChromaDB local + sentence-transformers

### Structured State Files (Context Engineering)

- Lightweight indices, just-in-time loading, not boot-time dump
- **Verdict: ADOPTED** — hierarchical context_index.md + .knowledge/ folder

### MCP TITAN 3-Tier Memory

- Short-term → Long-term → Archive with auto-promotion/demotion
- **Verdict: ADOPTED** — HOT/WARM/COLD tiers with access-count routing

### In Memoria (Codebase Pattern Learning)

- AST analysis, learns project structure, 17 MCP tools
- **Verdict: PARTIALLY ADOPTED** — codebase entity graph in Neo4j

### GLiNER (Zero-Shot Entity Extraction)

- Contrastive NER transformer, never hallucinates entities, CPU-only
- **Verdict: ADOPTED** — replaces LLM-based entity extraction

## Key Models Discovered

- **Qwen3-30B-A3B** — 30B total, 3B active per token. Best MoE efficiency ratio. ~8GB Q4.
- **GPT-OSS-20B** — OpenAI's open-weight MoE. 21B total, 3.6B active. ~14GB.
- **GLiNER** — Not an LLM. Dedicated NER via contrastive learning. ~200MB CPU.
- **all-MiniLM-L6-v2** — Industry standard embeddings. 22M params, 90MB, CPU.

## Decisions Made

- Use 3-specialist MoE (embedder + extractor + synthesizer), not a single monolithic model
- Use ChromaDB (local) instead of Neon pgvector (cloud)
- Use Neo4j Community Edition (Docker) instead of AuraDB (cloud)
- Total RAM budget: ~10GB active burst, fits 15-20GB allocation

## Benchmark Validation (2026-03-05)

### Embedding: MiniLM Wins on Domain Corpus

- Tested MiniLM vs E5-small-v2 vs BGE-small-en-v1.5 on actual `.knowledge/` data
- MiniLM: 8.9ms query, 100% Top-1, **0.46 discrimination** (4x better than E5)
- External benchmarks favoring E5 use generic datasets — our domain-specific corpus benefits from MiniLM's training diversity

### Entity Extraction: GLiNER v1 Right-Sized

- GLiNER2-large = 1.95GB download (10x current). Rejected — overkill for our corpus
- GLiNER v1 medium: ~200MB, ~210ms/text, 4 entities/text — works perfectly

### Synthesizer: Removed from Query Path

- Qwen3:8b @3.58 tok/s on CPU = 60-120s per query. Unacceptable for retrieval.
- **Architecture decision:** Pure retrieval engine. Calling LLM synthesizes from raw chunks.
- Qwen3:8b kept only for offline `memory_consolidate` (WARM→COLD digests).
- **RAM saved: 5.9GB. Query latency: 60s→<1s.**
