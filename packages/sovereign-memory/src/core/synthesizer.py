"""
Local LLM Synthesizer via Ollama

Replaces cloud Gemini/OpenAI/Anthropic synthesis with local Qwen3-30B-A3B.
On-demand loading — model loads when needed, unloads after 5 min idle.

Qwen3-30B-A3B is itself an MoE model (30B total, 3B active per token),
making this an MoE-within-MoE architecture.
"""

import logging
from typing import Optional

import httpx

from src.mcp.config import MODELS

logger = logging.getLogger(__name__)


class Synthesizer:
    """
    Local LLM synthesis via Ollama REST API.
    
    Used for two operations:
    1. Generating answers from retrieved context chunks
    2. Producing weekly consolidation digests
    """

    def __init__(
        self,
        host: str = None,
        model: str = None,
        keep_alive: str = None,
    ):
        self.host = host or MODELS.ollama_host
        self.model = model or MODELS.ollama_model
        self.keep_alive = keep_alive or MODELS.ollama_keep_alive
        self._client = httpx.Client(timeout=300.0)  # 5 min for first load

    def synthesize_answer(
        self,
        question: str,
        context_chunks: list[dict],
        system_prompt: str = None,
    ) -> str:
        """
        Generate an answer from retrieved context chunks.
        
        Args:
            question: The user's question.
            context_chunks: List of dicts with 'content' and optional 'metadata' keys.
            system_prompt: Optional system prompt override.
        
        Returns:
            The synthesized answer string.
        """
        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk.get("metadata", {}).get("source", "unknown")
            tier = chunk.get("tier", "unknown")
            content = chunk.get("content", "")
            context_parts.append(f"[{i}] (source: {source}, tier: {tier})\n{content}")
        
        context_text = "\n\n".join(context_parts)
        
        system = system_prompt or (
            "You are a precise memory retrieval assistant. "
            "Answer the question using ONLY the provided context. "
            "If the context doesn't contain enough information, say so clearly. "
            "Cite source numbers [1], [2] etc. when referencing specific context."
        )
        
        prompt = (
            f"Question: {question}\n\n"
            f"Context:\n{context_text}\n\n"
            f"Answer:"
        )
        
        return self._generate(prompt, system)

    def generate_digest(
        self,
        chunks: list[dict],
        time_period: str = "this week",
    ) -> str:
        """
        Generate a consolidation digest from a collection of memory chunks.
        Used for WARM → COLD tier consolidation.
        
        Args:
            chunks: List of chunk dicts to summarize.
            time_period: Human-readable description of the time period.
        
        Returns:
            A concise digest summarizing the chunks.
        """
        content_parts = []
        for chunk in chunks:
            source = chunk.get("metadata", {}).get("source", "unknown")
            content_parts.append(f"[{source}]: {chunk.get('content', '')}")
        
        all_content = "\n\n".join(content_parts)
        
        system = (
            "You are a knowledge consolidator. "
            "Create a concise but comprehensive digest of the provided memory fragments. "
            "Preserve key decisions, entities, metrics, and rationale. "
            "Group related items together. "
            "Use bullet points for clarity."
        )
        
        prompt = (
            f"Create a digest of the following memory fragments from {time_period}:\n\n"
            f"{all_content}\n\n"
            f"Digest:"
        )
        
        return self._generate(prompt, system)

    def _generate(self, prompt: str, system: str = "") -> str:
        """
        Send a generation request to the Ollama API.
        
        Uses the /api/generate endpoint with stream=false for simplicity.
        Ollama auto-loads the model on first request and keeps it for keep_alive duration.
        """
        try:
            response = self._client.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {
                        "num_ctx": 4096,
                        "temperature": 0.3,
                        "top_p": 0.9,
                    },
                    "keep_alive": self.keep_alive,
                },
            )
            response.raise_for_status()
            result = response.json()
            answer = result.get("response", "").strip()
            
            logger.info(
                f"Synthesis complete. "
                f"Tokens: {result.get('eval_count', '?')}, "
                f"Time: {result.get('total_duration', 0) / 1e9:.1f}s"
            )
            return answer
            
        except httpx.ConnectError:
            error_msg = (
                f"Cannot connect to Ollama at {self.host}. "
                "Ensure Ollama is running: 'ollama serve'"
            )
            logger.error(error_msg)
            return f"[Synthesis unavailable: {error_msg}]"
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                error_msg = (
                    f"Model '{self.model}' not found. "
                    f"Pull it first: 'ollama pull {self.model}'"
                )
                logger.error(error_msg)
                return f"[Synthesis unavailable: {error_msg}]"
            raise
            
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return f"[Synthesis error: {e}]"

    def is_available(self) -> bool:
        """Check if Ollama is reachable and the model exists."""
        try:
            response = self._client.get(f"{self.host}/api/tags")
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                available = any(self.model in m for m in models)
                if not available:
                    logger.warning(
                        f"Ollama running but model '{self.model}' not found. "
                        f"Available: {models}"
                    )
                return available
        except Exception:
            return False
        return False

    def close(self):
        """Close the HTTP client."""
        self._client.close()
