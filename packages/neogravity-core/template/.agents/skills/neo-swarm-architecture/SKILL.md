---
name: Neo Swarm Architecture
description: Deep technical context about the Neo Swarm Nexus codebase for when coding tasks or technical discussions arise.
---

# Neo Swarm Nexus Architecture Context

Load this skill when the user asks about Neo Swarm Nexus internals, when coding tasks reference the codebase, or when preparing technical interview answers.

> [!IMPORTANT]
> The old codebase at `d:\P-Projects\neo_swarm_nexus\` is **READ-ONLY**.
> All new work happens in `d:\P-Projects\profile-neo\neo-swarm-nexus\`.
> For full architecture details, read `profile-neo/neo-swarm-nexus/ARCHITECTURE.md`.
> Detailed architecture context (file locations, known issues, Rig B infra) was migrated to Sovereign Memory on 2026-03-05. Query with `memory_query("neo swarm architecture")` for deep details.

## System Overview

Neo Swarm Nexus is a split-compute AI trading ecosystem:
- **Local (Windows):** Data harvesting (Parquet), model training
- **Rig B (Cloud GPU, 164.52.193.16):** C++ Sentinel execution, ONNX inference, POSIX IPC

## Core Pipeline

```
Binance WS → live_oracle.py → /dev/shm/nexus_ipc (seqlock, 336 bytes, 100Hz)
  → sentinel_core (C++) → RSI regime routing → ONNX inference → 5 actions
```

## 40-Factor Tensor (STRICT)

| Slots | Content |
|---|---|
| [0-29] | L2 Depth: 10-level Bid/Ask, VWAP, Microprice, Imbalance |
| [30] | WS Latency (normalized) |
| [32] | **1m RSI** ← regime routing key |
| [33-34] | 1m BB Width, Position |
| [36] | **5m RSI** ← regime routing key |
| [37-38] | 5m BB Width, Position |

## Regime Routing (ADR-72)

| Condition | Expert | ONNX Model |
|---|---|---|
| `1m_RSI > 0.70 AND 5m_RSI > 0.70` | TRAP | `trap.onnx` |
| `1m_RSI < 0.30 AND 5m_RSI < 0.30` | BEAR | `bear.onnx` |
| Default | BULL | `bull.onnx` |

## Key Vocabulary (for interviews)

- **Zero-copy IPC** (not "shared memory")
- **Seqlock** (not "mutex" or "lock")
- **Mixture of Experts** (not "multiple models")
- **POSIX mmap** (not "file I/O")
- **Autonomic retrain loop** (not "cron job")
- **Hot-swap via SIGHUP** (not "restart")
