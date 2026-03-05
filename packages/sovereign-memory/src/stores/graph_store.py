"""
Neo4j Community Edition Graph Store

Entity-relationship knowledge graph for structured memory.
Adapted from the original neo4j_db.py driver wrapper — changed from AuraDB cloud
to local Docker CE, added entity-centric operations and relationship management.
"""

import logging
from typing import Optional
from neo4j import GraphDatabase

from src.mcp.config import STORES

logger = logging.getLogger(__name__)


class GraphStore:
    """
    Neo4j CE graph store for entity-relationship knowledge.
    
    Stores entities extracted by GLiNER and their relationships,
    enabling graph-based retrieval alongside vector search.
    """

    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None,
    ):
        uri = uri or STORES.neo4j_uri
        username = username or STORES.neo4j_username
        password = password or STORES.neo4j_password

        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Neo4j connection failed: {e}")
            raise

        # Ensure indexes exist for fast lookups
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create indexes on entity name and type for fast lookups."""
        with self.driver.session() as session:
            try:
                session.run(
                    "CREATE INDEX entity_name IF NOT EXISTS "
                    "FOR (e:Entity) ON (e.name)"
                )
                session.run(
                    "CREATE INDEX entity_type IF NOT EXISTS "
                    "FOR (e:Entity) ON (e.type)"
                )
                session.run(
                    "CREATE INDEX chunk_ref IF NOT EXISTS "
                    "FOR (e:Entity) ON (e.chunk_id)"
                )
                logger.info("Neo4j indexes ensured.")
            except Exception as e:
                logger.warning(f"Index creation skipped (may already exist): {e}")

    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed.")

    def upsert_entity(
        self,
        name: str,
        entity_type: str,
        chunk_id: str,
        source: str = "",
        properties: dict = None,
    ) -> dict:
        """
        Create or update an entity node. Uses MERGE to avoid duplicates.
        
        Returns the entity record.
        """
        props = properties or {}
        with self.driver.session() as session:
            result = session.run(
                """
                MERGE (e:Entity {name: $name, type: $type})
                ON CREATE SET
                    e.created_at = timestamp(),
                    e.chunk_id = $chunk_id,
                    e.source = $source,
                    e.mention_count = 1
                ON MATCH SET
                    e.mention_count = e.mention_count + 1,
                    e.last_seen_chunk = $chunk_id
                SET e += $props
                RETURN e {.name, .type, .mention_count, .chunk_id, .source} AS entity
                """,
                name=name,
                type=entity_type,
                chunk_id=chunk_id,
                source=source,
                props=props,
            )
            record = result.single()
            entity = dict(record["entity"]) if record else {}
            logger.info(f"Upserted entity: {entity_type}:{name}")
            return entity

    def create_relationship(
        self,
        from_name: str,
        from_type: str,
        to_name: str,
        to_type: str,
        rel_type: str,
        properties: dict = None,
    ) -> bool:
        """
        Create a relationship between two entities.
        Uses MERGE to avoid duplicate relationships.
        """
        props = properties or {}
        with self.driver.session() as session:
            try:
                session.run(
                    f"""
                    MATCH (a:Entity {{name: $from_name, type: $from_type}})
                    MATCH (b:Entity {{name: $to_name, type: $to_type}})
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r += $props, r.updated_at = timestamp()
                    """,
                    from_name=from_name,
                    from_type=from_type,
                    to_name=to_name,
                    to_type=to_type,
                    props=props,
                )
                logger.info(f"Relationship: {from_name} -[{rel_type}]-> {to_name}")
                return True
            except Exception as e:
                logger.error(f"Relationship creation failed: {e}")
                return False

    def find_entity(self, name: str, entity_type: str = None) -> list[dict]:
        """
        Find entities by name (case-insensitive partial match).
        Optionally filter by type.
        """
        with self.driver.session() as session:
            if entity_type:
                result = session.run(
                    """
                    MATCH (e:Entity)
                    WHERE toLower(e.name) CONTAINS toLower($name) AND e.type = $type
                    RETURN e {.name, .type, .mention_count, .chunk_id, .source} AS entity
                    LIMIT 20
                    """,
                    name=name,
                    type=entity_type,
                )
            else:
                result = session.run(
                    """
                    MATCH (e:Entity)
                    WHERE toLower(e.name) CONTAINS toLower($name)
                    RETURN e {.name, .type, .mention_count, .chunk_id, .source} AS entity
                    LIMIT 20
                    """,
                    name=name,
                )
            return [dict(record["entity"]) for record in result]

    def get_entity_neighborhood(
        self, name: str, entity_type: str = None, depth: int = 1
    ) -> dict:
        """
        Get an entity and its N-hop neighborhood (connected entities + relationships).
        This is the core GraphRAG retrieval operation.
        """
        with self.driver.session() as session:
            if entity_type:
                result = session.run(
                    f"""
                    MATCH (e:Entity {{name: $name, type: $type}})
                    OPTIONAL MATCH path = (e)-[r*1..{depth}]-(neighbor:Entity)
                    RETURN e {{.name, .type, .mention_count}} AS entity,
                           collect(DISTINCT neighbor {{.name, .type}}) AS neighbors,
                           [rel in collect(DISTINCT r) | type(rel[0])] AS relationship_types
                    """,
                    name=name,
                    type=entity_type,
                )
            else:
                result = session.run(
                    f"""
                    MATCH (e:Entity {{name: $name}})
                    OPTIONAL MATCH path = (e)-[r*1..{depth}]-(neighbor:Entity)
                    RETURN e {{.name, .type, .mention_count}} AS entity,
                           collect(DISTINCT neighbor {{.name, .type}}) AS neighbors,
                           [rel in collect(DISTINCT r) | type(rel[0])] AS relationship_types
                    """,
                    name=name,
                )
            record = result.single()
            if not record:
                return {"entity": None, "neighbors": [], "relationship_types": []}
            return {
                "entity": dict(record["entity"]),
                "neighbors": [dict(n) for n in record["neighbors"]],
                "relationship_types": record["relationship_types"],
            }

    def get_entities_for_chunk(self, chunk_id: str) -> list[dict]:
        """Get all entities that were extracted from a specific chunk."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (e:Entity)
                WHERE e.chunk_id = $chunk_id OR e.last_seen_chunk = $chunk_id
                RETURN e {.name, .type, .mention_count} AS entity
                """,
                chunk_id=chunk_id,
            )
            return [dict(record["entity"]) for record in result]

    def delete_entities_for_chunk(self, chunk_id: str) -> int:
        """Delete all entities (and their relationships) linked to a specific chunk."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (e:Entity {chunk_id: $chunk_id})
                DETACH DELETE e
                RETURN count(e) AS deleted
                """,
                chunk_id=chunk_id,
            )
            record = result.single()
            count = record["deleted"] if record else 0
            logger.info(f"Deleted {count} entities for chunk {chunk_id[:8]}...")
            return count

    def run_query(self, cypher: str, params: dict = None) -> list[dict]:
        """Run an arbitrary Cypher query (for advanced use)."""
        with self.driver.session() as session:
            result = session.run(cypher, params or {})
            return [dict(record) for record in result]

    def get_stats(self) -> dict:
        """Get entity and relationship counts."""
        with self.driver.session() as session:
            entities = session.run("MATCH (e:Entity) RETURN count(e) AS count")
            rels = session.run("MATCH ()-[r]->() RETURN count(r) AS count")
            return {
                "entities": entities.single()["count"],
                "relationships": rels.single()["count"],
            }
