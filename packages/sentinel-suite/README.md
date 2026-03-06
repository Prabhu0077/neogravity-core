# The Complete Sentinel Suite (NeoGravity + Sovereign Memory)

**Product Tier 3:** The Ultimate Autonomous Engineering Lab.

_Target Audience: Senior Architects, Elite Teams, and Quants._
_Price: $49/mo or $499/year._

## Overview

The Sentinel Suite is the combined powerhouse of the **NeoGravity OS** and the **Sovereign Memory Engine**. It provides true local autonomy: the Operating System executes workflows, pre-flights deployments, and enforces architectural guardrails, while the Sovereign Memory backend tracks every decision and system state change persistently.

## What's Included

When you purchase the Sentinel Suite, you receive two interconnected sub-systems:

1. **NeoGravity Core (The Agentic OS)**
   Installed globally via `npx @vibcoder/neogravity init`. It provides the `projects.json` registry, the `.knowledge` state machine, and the Powershell cron watchdogs.
2. **Sovereign Memory (The Brain)**
   Installed securely via our automated deployment script `install.ps1`. It provisions a robust, fully-local, containerized memory backend powered by Neo4j, ChromaDB, and GraphRAG.

## Installation

1. First, scaffold the Operating System into your active workspace:

   ```bash
   npx @vibcoder/neogravity init
   ```

2. Second, navigate to the `memory` folder and run the backend installer:

   ```powershell
   .\install.ps1
   ```

3. Hook your AI Assistant (Cursor, Claude) into the newly generated MCP configuration block.

## Documentation

For full guides on writing custom Skills, configuring Workflow paths, or tuning the MoE routing thresholds, please visit [docs.vibcoder.com](https://docs.vibcoder.com).
