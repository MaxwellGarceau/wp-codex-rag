"""
HTML cleaning utility for processing WordPress documentation content.

This module provides a dedicated HTMLCleaner class that handles the conversion
of HTML content to clean, structured plain text suitable for embedding and
vector database storage.
"""

import re

from bs4 import BeautifulSoup

from core.logging_config import get_logger

logger = get_logger(__name__)


class HTMLCleaner:
    """
    Utility class for cleaning HTML content and converting to structured plain text.

    This class is specifically designed to handle WordPress documentation HTML
    and convert it to clean text while preserving important structural elements
    like headings, lists, code blocks, and links.

    Features:
    - Removes HTML tags while preserving content structure
    - Converts headings to markdown-style format
    - Handles lists (ordered and unordered) with proper formatting
    - Preserves code blocks with backticks
    - Converts links to plain text with URLs
    - Handles WordPress-specific elements (notes, warnings, etc.)
    - Cleans whitespace and normalizes line breaks
    - Provides fallback handling for malformed HTML
    """

    def __init__(self) -> None:
        """Initialize the HTML cleaner."""
        logger.debug("HTMLCleaner initialized")

    def clean_html(self, html_content: str) -> str:
        """
        Clean HTML content and convert to plain text while preserving structure.

        Args:
            html_content: Raw HTML content from WordPress API

        Returns:
            Cleaned plain text with preserved structure
        """
        if not html_content or not html_content.strip():
            return ""

        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script and style elements completely
            for script in soup(["script", "style"]):
                script.decompose()

            # Handle WordPress-specific elements
            self._handle_wordpress_elements(soup)

            # Convert headings to plain text with clear hierarchy
            self._convert_headings(soup)

            # Convert lists to plain text
            self._convert_lists(soup)

            # Convert code blocks to plain text
            self._convert_code_blocks(soup)

            # Convert links to plain text with URL
            self._convert_links(soup)

            # Convert paragraphs to plain text with line breaks
            self._convert_paragraphs(soup)

            # Convert line breaks
            self._convert_line_breaks(soup)

            # Get the final text and clean it up
            text = soup.get_text()
            return self._normalize_whitespace(text)

        except Exception as e:
            logger.warning(f"Error cleaning HTML content: {e}")
            return self._fallback_clean(html_content)

    def _handle_wordpress_elements(self, soup: BeautifulSoup) -> None:
        """Handle WordPress-specific elements like note boxes and warnings."""
        for note in soup.find_all(
            ["div"], class_=["wp-block-group", "wp-block-column"]
        ):
            # Check if it's a note or warning box
            if any(
                keyword in note.get_text().lower()
                for keyword in ["note:", "warning:", "important:", "tip:"]
            ):
                note_text = note.get_text().strip()
                if note_text:
                    note.replace_with(f"\n{note_text}\n")

    def _convert_headings(self, soup: BeautifulSoup) -> None:
        """Convert headings to plain text with clear hierarchy."""
        for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            level = int(heading.name[1])
            heading_text = heading.get_text().strip()
            if heading_text:
                # Add clear heading markers
                heading.replace_with(f"\n{'#' * level} {heading_text}\n")

    def _convert_lists(self, soup: BeautifulSoup) -> None:
        """Convert lists to plain text with proper formatting."""
        # Handle unordered lists
        for ul in soup.find_all("ul"):
            for li in ul.find_all("li"):
                li_text = li.get_text().strip()
                if li_text:
                    li.replace_with(f"• {li_text}\n")
            ul.unwrap()

        # Handle ordered lists
        for ol in soup.find_all("ol"):
            for i, li in enumerate(ol.find_all("li"), 1):
                li_text = li.get_text().strip()
                if li_text:
                    li.replace_with(f"{i}. {li_text}\n")
            ol.unwrap()

    def _convert_code_blocks(self, soup: BeautifulSoup) -> None:
        """Convert code blocks to plain text with backticks."""
        for code in soup.find_all(["code", "pre"]):
            code_text = code.get_text().strip()
            if code_text:
                code.replace_with(f"`{code_text}`")

    def _convert_links(self, soup: BeautifulSoup) -> None:
        """Convert links to plain text with URL."""
        for link in soup.find_all("a"):
            link_text = link.get_text().strip()
            href = link.get("href", "")
            if link_text and href:
                link.replace_with(f"{link_text} ({href})")
            elif link_text:
                link.replace_with(link_text)

    def _convert_paragraphs(self, soup: BeautifulSoup) -> None:
        """Convert paragraphs to plain text with line breaks."""
        for p in soup.find_all("p"):
            p_text = p.get_text().strip()
            if p_text:
                p.replace_with(f"{p_text}\n\n")

    def _convert_line_breaks(self, soup: BeautifulSoup) -> None:
        """Convert line breaks to newlines."""
        for br in soup.find_all("br"):
            br.replace_with("\n")

    def _normalize_whitespace(self, text: str) -> str:
        """Clean up extra whitespace and normalize line breaks."""
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            # Strip whitespace from each line
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
            elif (
                cleaned_lines and cleaned_lines[-1]
            ):  # Only add empty line if previous line wasn't empty
                cleaned_lines.append("")

        # Join lines and clean up multiple consecutive newlines
        result = "\n".join(cleaned_lines)

        # Replace multiple consecutive newlines with double newlines
        result = re.sub(r"\n{3,}", "\n\n", result)

        return result.strip()

    def _fallback_clean(self, html_content: str) -> str:
        """Fallback HTML cleaning using regex when BeautifulSoup fails."""
        # Remove HTML tags but keep the text content
        clean_text = re.sub(r"<[^>]+>", "", html_content)
        # Clean up extra whitespace
        clean_text = re.sub(r"\s+", " ", clean_text)
        return clean_text.strip()
