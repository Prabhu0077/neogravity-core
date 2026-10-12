"""
GLiNER Entity Extractor

Extractive Named Entity Recognition (it can only return text that is in the input) using contrastive learning.
Replaces the placeholder heuristic in the original ingestion_service.py (L42-71)
that just split on uppercase words.

GLiNER matches text spans to entity type embeddings — it can only select
substrings that EXIST in the input. It never generates or hallucinates entities.

Model: urchade/gliner_medium-v2.1 (~200MB, CPU)
"""

import logging
from dataclasses import dataclass, field

from src.mcp.config import MODELS

logger = logging.getLogger(__name__)

# Lazy-loaded singleton
_model = None


@dataclass
class ExtractedEntity:
    """A single extracted entity with its metadata."""
    text: str              # The exact substring from source text
    label: str             # Entity type (person, organization, etc.)
    score: float           # Confidence score (0-1)
    start: int             # Character start position in source text
    end: int               # Character end position in source text


@dataclass
class ExtractionResult:
    """Result of entity extraction from a text chunk."""
    entities: list[ExtractedEntity] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)  # Inferred co-occurrence


def _get_model():
    """Lazy-load the GLiNER model."""
    global _model
    if _model is None:
        from gliner import GLiNER
        logger.info(f"Loading GLiNER model: {MODELS.gliner_model}...")
        _model = GLiNER.from_pretrained(MODELS.gliner_model)
        logger.info("GLiNER model loaded.")
    return _model


def extract_entities(
    text: str,
    entity_types: list[str] = None,
    threshold: float = 0.5,
) -> ExtractionResult:
    """
    Extract entities from text using GLiNER.
    
    Args:
        text: Source text to extract entities from.
        entity_types: List of entity types to detect. 
                      Defaults to config.MODELS.entity_types.
        threshold: Minimum confidence score (0-1) for entity inclusion.
    
    Returns:
        ExtractionResult with entities and inferred relationships.
    """
    model = _get_model()
    types = entity_types or MODELS.entity_types
    
    # GLiNER predict_entities returns list of dicts:
    # [{"text": "Alice", "label": "person", "score": 0.98, "start": 0, "end": 5}]
    raw_entities = model.predict_entities(text, types, threshold=threshold)
    
    # Deduplicate by (text, label) — keep highest score
    seen = {}
    for ent in raw_entities:
        key = (ent["text"].lower(), ent["label"])
        if key not in seen or ent["score"] > seen[key]["score"]:
            seen[key] = ent
    
    entities = [
        ExtractedEntity(
            text=ent["text"],
            label=ent["label"],
            score=ent["score"],
            start=ent.get("start", 0),
            end=ent.get("end", 0),
        )
        for ent in seen.values()
    ]
    
    # Infer co-occurrence relationships:
    # If two entities appear in the same text chunk, they are related
    relationships = []
    for i, ent_a in enumerate(entities):
        for ent_b in entities[i + 1:]:
            if ent_a.label != ent_b.label or ent_a.text != ent_b.text:
                relationships.append({
                    "from_name": ent_a.text,
                    "from_type": ent_a.label,
                    "to_name": ent_b.text,
                    "to_type": ent_b.label,
                    "rel_type": "CO_OCCURS_WITH",
                    "properties": {"source": "extraction"},
                })
    
    logger.info(
        f"Extracted {len(entities)} entities, "
        f"{len(relationships)} relationships from {len(text)} chars"
    )
    
    return ExtractionResult(entities=entities, relationships=relationships)


def extract_entities_batch(
    texts: list[str],
    entity_types: list[str] = None,
    threshold: float = 0.5,
) -> list[ExtractionResult]:
    """Extract entities from multiple texts."""
    return [extract_entities(t, entity_types, threshold) for t in texts]
