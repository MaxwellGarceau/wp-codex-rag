import re
from typing import Any

from core.logging_config import get_logger

logger = get_logger(__name__)


class SemanticChunker:
    """
    Semantic chunking utility for WordPress documentation.

    This class provides intelligent text chunking that:
    - Uses heading levels as primary boundaries
    - Preserves complete code blocks
    - Falls back to paragraphs and sentences for large content
    - Ensures optimal chunk sizes for embedding models
    """

    def __init__(self) -> None:
        """Initialize the semantic chunker."""
        logger.debug("SemanticChunker initialized")

    def chunk_text(self, text: str) -> list[str]:
        """
        Semantic chunking optimized for WordPress documentation.

        Strategy:
        1. Preserve complete code blocks
        2. Use H3 headings as primary boundaries
        3. Fall back to paragraphs for large sections
        4. Fall back to sentences for very long paragraphs
        5. Ensure chunks stay within optimal size limits

        Args:
            text: The cleaned text to chunk

        Returns:
            List of semantically coherent text chunks
        """
        if not text.strip():
            return []

        logger.debug("Starting semantic chunking process")

        # Step 1: Extract and preserve code blocks
        code_blocks, text_without_code = self._remove_code_blocks(text)

        # Step 2: Parse heading structure
        sections = self._parse_heading_structure(text_without_code)

        # Step 3: Process sections into chunks
        chunks = []
        for section in sections:
            section_chunks = self._process_section(section)
            chunks.extend(section_chunks)

        # Step 4: Re-insert code blocks
        chunks = self._merge_code_blocks(chunks, code_blocks)

        # Step 5: Final validation and cleanup
        chunks = self._validate_chunk_sizes(chunks)

        logger.debug(f"Semantic chunking complete: {len(chunks)} chunks generated")
        return chunks

    def _extract_code_blocks(self, text: str) -> tuple[list[dict[str, str]], str]:
        """
        Extract code blocks from text and return them with metadata.

        Returns:
            Tuple of (code_blocks_list, text_with_placeholders)
        """
        code_blocks = []

        # Pattern to match code blocks (```code``` or `inline code`)
        code_pattern = r"```([^`]*?)```|`([^`\n]+)`"

        def replace_code_block(match):
            full_match = match.group(0)
            if full_match.startswith("```"):
                # Multi-line code block
                content = match.group(1) or ""
                placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"
                code_blocks.append(
                    {
                        "content": f"```{content}```",
                        "placeholder": placeholder,
                        "type": "multiline",
                    }
                )
            else:
                # Inline code
                content = match.group(2) or ""
                placeholder = f"__INLINE_CODE_{len(code_blocks)}__"
                code_blocks.append(
                    {
                        "content": f"`{content}`",
                        "placeholder": placeholder,
                        "type": "inline",
                    }
                )
            return placeholder

        text_with_placeholders = re.sub(code_pattern, replace_code_block, text)
        return code_blocks, text_with_placeholders

    def _remove_code_blocks(self, text: str) -> tuple[list[dict[str, str]], str]:
        """Remove code blocks from text, replacing with placeholders."""
        return self._extract_code_blocks(text)

    def _parse_heading_structure(self, text: str) -> list[dict[str, Any]]:
        """
        Parse text into sections based on heading levels.

        Returns:
            List of section dictionaries with 'level', 'title', 'content', and 'children'
        """
        sections = []
        current_section = None

        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line is a heading (## Title format from HTMLCleaner)
            if line.startswith("##"):
                # Save previous section if exists
                if current_section:
                    sections.append(current_section)

                # Start new section
                level = line.count("#")
                title = line.lstrip("#").strip()
                current_section = {
                    "level": level,
                    "title": title,
                    "content": line + "\n",
                    "children": [],
                }
            else:
                # Add content to current section
                if current_section:
                    current_section["content"] += line + "\n"
                else:
                    # Content before any heading - create a root section
                    if not sections or sections[-1]["level"] != 0:
                        sections.append(
                            {
                                "level": 0,
                                "title": "Introduction",
                                "content": line + "\n",
                                "children": [],
                            }
                        )
                    else:
                        sections[-1]["content"] += line + "\n"

        # Add final section
        if current_section:
            sections.append(current_section)

        return sections

    def _process_section(self, section: dict[str, Any]) -> list[str]:
        """
        Process a section into appropriate chunks based on size and content.

        Args:
            section: Section dictionary with level, title, content, children

        Returns:
            List of chunks for this section
        """
        content = section["content"].strip()
        if not content:
            return []

        # Determine optimal chunking strategy based on section level and size
        if section["level"] == 0:  # Introduction content
            return self._chunk_by_paragraphs(content, max_size=1500)
        elif section["level"] == 1:  # H1 - usually too large
            return self._chunk_by_paragraphs(content, max_size=2000)
        elif section["level"] == 2:  # H2 - check size
            if len(content) <= 2000:
                return [content]
            else:
                return self._chunk_by_paragraphs(content, max_size=1500)
        elif section["level"] == 3:  # H3 - usually optimal
            if len(content) <= 1500:
                return [content]
            else:
                return self._chunk_by_paragraphs(content, max_size=1200)
        else:  # H4+ - usually small, but check size
            if len(content) <= 1000:
                return [content]
            else:
                return self._chunk_by_paragraphs(content, max_size=800)

    def _chunk_by_paragraphs(self, text: str, max_size: int = 1500) -> list[str]:
        """
        Split text by paragraphs, respecting size limits.

        Args:
            text: Text to chunk
            max_size: Maximum size per chunk

        Returns:
            List of paragraph-based chunks
        """
        chunks = []
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        current_chunk = ""

        for paragraph in paragraphs:
            # If adding this paragraph would exceed max_size, start new chunk
            if current_chunk and len(current_chunk) + len(paragraph) + 2 > max_size:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        # Check if any chunks are still too large and split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > max_size:
                final_chunks.extend(self._chunk_by_sentences(chunk, max_size))
            else:
                final_chunks.append(chunk)

        return final_chunks

    def _chunk_by_sentences(self, text: str, max_size: int = 1000) -> list[str]:
        """
        Split text by sentences as a last resort for very long content.

        Args:
            text: Text to chunk
            max_size: Maximum size per chunk

        Returns:
            List of sentence-based chunks
        """
        # Simple sentence splitting - could be enhanced with NLP libraries
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # If adding this sentence would exceed max_size, start new chunk
            if current_chunk and len(current_chunk) + len(sentence) + 1 > max_size:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _merge_code_blocks(
        self, chunks: list[str], code_blocks: list[dict[str, str]]
    ) -> list[str]:
        """
        Re-insert code blocks back into chunks.

        Args:
            chunks: List of text chunks
            code_blocks: List of code block dictionaries

        Returns:
            Chunks with code blocks restored
        """
        if not code_blocks:
            return chunks

        # Create mapping of placeholders to content
        code_map = {block["placeholder"]: block["content"] for block in code_blocks}

        # Replace placeholders in all chunks
        restored_chunks = []
        for chunk in chunks:
            restored_chunk = chunk
            for placeholder, content in code_map.items():
                restored_chunk = restored_chunk.replace(placeholder, content)
            restored_chunks.append(restored_chunk)

        return restored_chunks

    def _validate_chunk_sizes(self, chunks: list[str]) -> list[str]:
        """
        Final validation of chunk sizes and cleanup.

        Args:
            chunks: List of chunks to validate

        Returns:
            Validated and cleaned chunks
        """
        validated_chunks = []

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue

            # Skip chunks that are too small (less than 50 characters)
            if len(chunk) < 50:
                logger.debug(
                    f"Skipping chunk too small ({len(chunk)} chars): {chunk[:50]}..."
                )
                continue

            # Log chunks that are very large (over 2000 characters)
            if len(chunk) > 2000:
                logger.warning(
                    f"Chunk larger than recommended ({len(chunk)} chars): {chunk[:100]}..."
                )

            validated_chunks.append(chunk)

        return validated_chunks
