# MoE Model Selection — March 2026

## Use Case
Local LLM inference for Antigravity's memory system: entity extraction, synthesis, and summarization.

## Hardware Budget
- 40GB total RAM, 15-20GB available for memory system
- No dedicated GPU (CPU inference via Ollama + GGUF quantization)

## Models Evaluated

### MoE Models (Sparse — only activate subset of params)
| Model | Total Params | Active/Token | RAM (Q4) | Structured JSON | Ollama |
|-------|-------------|-------------|----------|----------------|--------|
| **Qwen3-30B-A3B** ⭐ | 30B | 3B | ~8GB | ✅ Native | ✅ |
| GPT-OSS-20B | 21B | 3.6B | ~14GB | ✅ Native | ✅ |
| Qwen3-Coder-Next 80B-A3B | 80B | 3B | ~8GB | ✅ function calling | ✅ |
| Mixtral 8x7B | 46.7B | 12.9B | ~26GB | ✅ via grammar | ✅ |
| GLM-4.7-Flash | 30B MoE | ? | ? | ? | ? |

### Dense Models (Backup)
| Model | Params | RAM (Q4) | Best For | Ollama |
|-------|--------|----------|----------|--------|
| Llama 3.1 8B | 8B | ~4.8GB | RAG, 128K context | ✅ |
| Phi-3 Mini | 3.8B | ~2GB | Instruction following | ✅ |
| Gemma 3 4B | 4B | ~3.3GB | Multimodal, 128K | ✅ |
| Gemma 3 12B | 12B | ~8.1GB | Stronger reasoning | ✅ |

### Specialized (Non-LLM)
| Model | Type | RAM | Best For |
|-------|------|-----|----------|
| **GLiNER** ⭐ | Contrastive NER | ~200MB | Zero-hallucination entity extraction |
| **all-MiniLM-L6-v2** ⭐ | Sentence Transformer | ~90MB | Text embeddings (384-dim) |

## Final Selection: 3-Specialist Architecture
1. **Embedder:** all-MiniLM-L6-v2 (always loaded, 90MB)
2. **Extractor:** GLiNER (always loaded, 200MB)
3. **Synthesizer:** Qwen3-30B-A3B (on-demand, ~8GB, unloads after 5min idle)

## Why Not Single Model?
- A single 7b+ model is always loaded → wastes 5-8GB RAM even when idle
- Specialists are purpose-built → higher accuracy per task
- MoE router is plain Python if/else → zero overhead
- Mirrors Neo Swarm Nexus's Sentinel specialist architecture (Bull/Bear/Trap)
