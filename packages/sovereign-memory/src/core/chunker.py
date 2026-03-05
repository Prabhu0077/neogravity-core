"""
Markdown-Aware Text Chunker

Adapts RecursiveCharacterTextSplitter from the original ingestion_service.py
with markdown-aware splitting — respects header boundaries to keep sections intact.
"""

import logging
import re
from dataclasses import dataclass

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from src.mcp.config import CHUNKER

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """A text chunk with its metadata."""
    content: str
    index: int              # Position in original document
    source: str             # Source file/document name
    section_header: str     # Nearest markdown header (if any)


def chunk_text(
    text: str,
    source: str = "unknown",
    chunk_size: int = None,
    chunk_overlap: int = None,
    markdown_aware: bool = None,
) -> list[Chunk]:
    """
    Split text into chunks for embedding and storage.
    
    If markdown_aware is True (default), splits on markdown headers first,
    then applies character-level splitting within each section.
    This keeps related content together within sections.
    
    Args:
        text: The full text to chunk.
        source: Source identifier for metadata.
        chunk_size: Max characters per chunk (default from config).
        chunk_overlap: Character overlap between chunks (default from config).
        markdown_aware: Whether to respect markdown headers (default from config).
    
    Returns:
        List of Chunk objects ready for embedding.
    """
    chunk_size = chunk_size or CHUNKER.chunk_size
    chunk_overlap = chunk_overlap or CHUNKER.chunk_overlap
    markdown_aware = markdown_aware if markdown_aware is not None else CHUNKER.markdown_aware

    if markdown_aware and _has_markdown_headers(text):
        return _markdown_split(text, source, chunk_size, chunk_overlap)
    else:
        return _plain_split(text, source, chunk_size, chunk_overlap)


def _has_markdown_headers(text: str) -> bool:
    """Check if text contains markdown headers."""
    return bool(re.search(r"^#{1,4}\s+", text, re.MULTILINE))


def _markdown_split(
    text: str, source: str, chunk_size: int, chunk_overlap: int
) -> list[Chunk]:
    """
    Two-pass splitting:
    1. Split on markdown headers to preserve section structure
    2. Within each section, apply character-level splitting if too long
    """
    # Pass 1: Split by markdown headers
    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
        ("####", "h4"),
    ]
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )
    md_sections = md_splitter.split_text(text)

    # Pass 2: Character-level split within sections
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = []
    for section in md_sections:
        section_text = section.page_content
        section_header = " > ".join(
            v for k, v in sorted(section.metadata.items())
        ) or ""
        
        if len(section_text) <= chunk_size:
            chunks.append(Chunk(
                content=section_text,
                index=len(chunks),
                source=source,
                section_header=section_header,
            ))
        else:
            sub_chunks = char_splitter.split_text(section_text)
            for sub in sub_chunks:
                chunks.append(Chunk(
                    content=sub,
                    index=len(chunks),
                    source=source,
                    section_header=section_header,
                ))

    logger.info(
        f"Markdown-aware chunking: {len(text)} chars → {len(chunks)} chunks "
        f"(source={source})"
    )
    return chunks


def _plain_split(
    text: str, source: str, chunk_size: int, chunk_overlap: int
) -> list[Chunk]:
    """Simple character-level splitting for non-markdown text."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    raw_chunks = splitter.split_text(text)
    
    chunks = [
        Chunk(content=c, index=i, source=source, section_header="")
        for i, c in enumerate(raw_chunks)
    ]
    
    logger.info(
        f"Plain chunking: {len(text)} chars → {len(chunks)} chunks "
        f"(source={source})"
    )
    return chunks
