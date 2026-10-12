"""
Hybrid-RAG Memory Server Configuration

Central config for all memory system parameters.
Tier thresholds, decay rates, model paths, and store connections.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class TierConfig:
    """Memory tier promotion/demotion thresholds."""
    hot_max_age_days: int = int(os.getenv("HOT_MAX_AGE_DAYS", "7"))
    warm_max_age_days: int = int(os.getenv("WARM_MAX_AGE_DAYS", "30"))
    hot_min_access_count: int = 3       # Promote WARM→HOT after 3 accesses within window
    cold_after_days: int = 90           # Archive to COLD after 90 days untouched


@dataclass(frozen=True)
class DecayConfig:
    """Temporal decay scoring parameters."""
    lambda_decay: float = float(os.getenv("DECAY_LAMBDA", "0.05"))
    # Score = exp(-lambda * days_since_last_access)
    # At lambda=0.05: 7 days → 0.70, 14 days → 0.50, 30 days → 0.22


@dataclass(frozen=True)
class SurpriseConfig:
    """Contradiction detection thresholds."""
    cosine_threshold: float = float(os.getenv("SURPRISE_THRESHOLD", "0.85"))
    # If two chunks have cosine similarity > threshold but different content → flag


@dataclass(frozen=True)
class ModelConfig:
    """Local model paths and Ollama settings."""
    # Specialist 1: Embedder (always loaded, ~90MB)
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embedding_dim: int = 384

    # Specialist 2: Extractor (always loaded, ~200MB)
    gliner_model: str = os.getenv("GLINER_MODEL", "urchade/gliner_medium-v2.1")
    entity_types: list = field(default_factory=lambda: [
        "person", "organization", "project", "technology",
        "product", "decision", "metric", "date", "location"
    ])

    # Specialist 3: Synthesizer (on-demand, ~8GB Q4)
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    ollama_keep_alive: str = "5m"  # Unload after 5 min idle


@dataclass(frozen=True)
class StoreConfig:
    """Data store connection parameters."""
    # ChromaDB (embedded, no server needed)
    chroma_persist_path: str = os.getenv("CHROMA_PERSIST_PATH", "./data/chroma")
    chroma_collection_hot: str = "memory_hot"
    chroma_collection_warm: str = "memory_warm"
    chroma_collection_cold: str = "memory_cold"

    # Neo4j Community Edition (Docker)
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    # No default on purpose: set NEO4J_PASSWORD in your environment or .env file.
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")


@dataclass(frozen=True)
class ChunkerConfig:
    """Text chunking parameters."""
    chunk_size: int = 500
    chunk_overlap: int = 50
    markdown_aware: bool = True  # Respect markdown headers as split boundaries


# Singleton config instances
TIER = TierConfig()
DECAY = DecayConfig()
SURPRISE = SurpriseConfig()
MODELS = ModelConfig()
STORES = StoreConfig()
CHUNKER = ChunkerConfig()
