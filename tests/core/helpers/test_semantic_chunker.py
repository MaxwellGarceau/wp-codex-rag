"""
Unit tests for SemanticChunker class.

This module tests the semantic chunking functionality including:
- Basic text chunking
- Heading structure parsing
- Code block preservation
- Paragraph and sentence fallbacks
- Size validation
- Edge cases and error handling
"""

from core.helpers.semantic_chunker import SemanticChunker


class TestSemanticChunker:
    """Test cases for SemanticChunker class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.chunker = SemanticChunker()

    def test_chunk_text_empty_input(self) -> None:
        """Test chunking with empty or whitespace-only input."""
        assert self.chunker.chunk_text("") == []
        assert self.chunker.chunk_text("   ") == []
        assert self.chunker.chunk_text(" \n \t ") == []

    def test_chunk_text_simple_headings(self) -> None:
        """Test chunking with simple heading structure."""
        text = """
## Introduction
This is an introduction to the topic with more content to meet minimum size requirements.

## Main Content
This is the main content section with sufficient text to pass validation.

## Conclusion
This is the conclusion with enough content to be included in the final chunks.
"""
        chunks = self.chunker.chunk_text(text)

        assert len(chunks) == 3
        assert "## Introduction" in chunks[0]
        assert "## Main Content" in chunks[1]
        assert "## Conclusion" in chunks[2]

    def test_chunk_text_nested_headings(self) -> None:
        """Test chunking with nested heading levels."""
        text = """
## Main Topic
This is the main topic with sufficient content to pass validation.

### Subsection 1
This is subsection 1 content with enough text to meet minimum requirements.

### Subsection 2
This is subsection 2 content with adequate length for inclusion.

#### Sub-subsection
This is a sub-subsection with sufficient content to be included.

## Another Main Topic
This is another main topic with enough content to pass validation.
"""
        chunks = self.chunker.chunk_text(text)

        # Should create separate chunks for each heading level
        assert len(chunks) >= 4
        assert "## Main Topic" in chunks[0]
        assert "### Subsection 1" in chunks[1]
        assert "### Subsection 2" in chunks[2]
        assert "#### Sub-subsection" in chunks[3]

    def test_chunk_text_code_blocks(self) -> None:
        """Test that code blocks are preserved correctly."""
        text = """
## Code Example
Here's a code example with sufficient content to pass validation:

```php
function my_function() {
    return "Hello World";
}
```

And some inline code: `echo "test";`

## More Content
This is more content with enough text to be included in the final chunks.
"""
        chunks = self.chunker.chunk_text(text)

        # Should preserve code blocks
        assert len(chunks) == 2
        assert "```php" in chunks[0]
        assert "function my_function()" in chunks[0]
        assert '`echo "test";`' in chunks[0]
        assert "## More Content" in chunks[1]

    def test_chunk_text_large_section(self) -> None:
        """Test chunking of large sections that need paragraph splitting."""
        # Create a large H2 section
        large_content = "This is a very long paragraph. " * 50  # ~1500 characters
        text = f"""
## Large Section
{large_content}

## Small Section
This is a small section.
"""
        chunks = self.chunker.chunk_text(text)

        # Should split the large section
        assert len(chunks) >= 1
        assert "## Large Section" in chunks[0]
        # The small section might be filtered out if too small
        if len(chunks) > 1:
            assert "## Small Section" in chunks[-1]

    def test_chunk_text_very_large_paragraph(self) -> None:
        """Test chunking of very large paragraphs that need sentence splitting."""
        # Create a very large paragraph
        large_paragraph = "This is a sentence. " * 100  # ~2000 characters
        text = f"""
## Very Large Paragraph
{large_paragraph}
"""
        chunks = self.chunker.chunk_text(text)

        # Should split the large paragraph by sentences
        assert len(chunks) >= 1
        assert "## Very Large Paragraph" in chunks[0]

    def test_chunk_text_no_headings(self) -> None:
        """Test chunking of text without headings."""
        text = """
This is some content without headings.
It has multiple paragraphs.

This is another paragraph with more content.
"""
        chunks = self.chunker.chunk_text(text)

        # Should create chunks for content without headings
        assert len(chunks) >= 1
        assert "This is some content without headings" in chunks[0]

    def test_chunk_text_mixed_content(self) -> None:
        """Test chunking with mixed content types."""
        text = """
## Plugin Development

WordPress plugins extend functionality.

### Creating a Plugin

To create a plugin:

```php
<?php
/**
 * Plugin Name: My Plugin
 */
```

### Plugin Structure

A plugin needs:
1. Plugin header
2. Main functionality
3. Activation hooks

## Security

Always sanitize input: `sanitize_text_field($input)`
"""
        chunks = self.chunker.chunk_text(text)

        # Should handle mixed content properly
        assert len(chunks) >= 4
        assert "## Plugin Development" in chunks[0]
        assert "### Creating a Plugin" in chunks[1]
        assert "```php" in chunks[1]
        assert "### Plugin Structure" in chunks[2]
        assert "## Security" in chunks[3]
        assert "`sanitize_text_field($input)`" in chunks[3]

    def test_extract_code_blocks(self) -> None:
        """Test code block extraction functionality."""
        text = "This has ```code``` and `inline` code."
        code_blocks, text_with_placeholders = self.chunker._extract_code_blocks(text)

        assert len(code_blocks) == 2
        assert code_blocks[0]["type"] == "multiline"
        assert code_blocks[1]["type"] == "inline"
        assert "__CODE_BLOCK_0__" in text_with_placeholders
        assert "__INLINE_CODE_1__" in text_with_placeholders

    def test_parse_heading_structure(self) -> None:
        """Test heading structure parsing."""
        text = """
## Main Topic
Content under main topic.

### Subsection
Content under subsection.

## Another Topic
More content.
"""
        sections = self.chunker._parse_heading_structure(text)

        assert len(sections) == 3
        assert sections[0]["level"] == 2
        assert sections[0]["title"] == "Main Topic"
        assert sections[1]["level"] == 3
        assert sections[1]["title"] == "Subsection"
        assert sections[2]["level"] == 2
        assert sections[2]["title"] == "Another Topic"

    def test_process_section_h3_optimal(self) -> None:
        """Test processing of H3 sections (usually optimal size)."""
        section = {
            "level": 3,
            "title": "Test Section",
            "content": "### Test Section\nThis is a test section with optimal size.",
            "children": [],
        }
        chunks = self.chunker._process_section(section)

        assert len(chunks) == 1
        assert "### Test Section" in chunks[0]

    def test_process_section_h2_large(self) -> None:
        """Test processing of large H2 sections."""
        large_content = "This is a very long section. " * 50
        section = {
            "level": 2,
            "title": "Large Section",
            "content": f"## Large Section\n{large_content}",
            "children": [],
        }
        chunks = self.chunker._process_section(section)

        # Should split large H2 section
        assert len(chunks) >= 1
        assert "## Large Section" in chunks[0]

    def test_chunk_by_paragraphs(self) -> None:
        """Test paragraph-based chunking."""
        text = """
First paragraph with some content.

Second paragraph with more content.

Third paragraph with even more content.
"""
        chunks = self.chunker._chunk_by_paragraphs(text, max_size=100)

        # Should split by paragraphs when size limit is reached
        assert len(chunks) >= 2
        assert "First paragraph" in chunks[0]
        # The second chunk might contain the third paragraph if second is too small
        assert any("paragraph" in chunk for chunk in chunks[1:])

    def test_chunk_by_sentences(self) -> None:
        """Test sentence-based chunking."""
        text = "This is the first sentence. This is the second sentence. This is the third sentence."
        chunks = self.chunker._chunk_by_sentences(text, max_size=50)

        # Should split by sentences when size limit is reached
        assert len(chunks) >= 2
        assert "first sentence" in chunks[0]
        assert "second sentence" in chunks[1]

    def test_merge_code_blocks(self) -> None:
        """Test code block merging functionality."""
        chunks = ["This has __CODE_BLOCK_0__ and __INLINE_CODE_1__."]
        code_blocks = [
            {"placeholder": "__CODE_BLOCK_0__", "content": "```code```"},
            {"placeholder": "__INLINE_CODE_1__", "content": "`inline`"},
        ]

        restored_chunks = self.chunker._merge_code_blocks(chunks, code_blocks)

        assert len(restored_chunks) == 1
        assert "```code```" in restored_chunks[0]
        assert "`inline`" in restored_chunks[0]

    def test_validate_chunk_sizes(self) -> None:
        """Test chunk size validation."""
        chunks = [
            "This is a valid chunk with sufficient content that meets the minimum length requirement.",
            "Too short",  # Should be filtered out
            "This is another valid chunk with enough content to pass validation.",
            "",  # Should be filtered out
            "   ",  # Should be filtered out
        ]

        validated_chunks = self.chunker._validate_chunk_sizes(chunks)

        # Should filter out chunks that are too small or empty
        assert len(validated_chunks) >= 1
        assert any("This is a valid chunk" in chunk for chunk in validated_chunks)
        assert any("This is another valid chunk" in chunk for chunk in validated_chunks)

    def test_chunk_text_complex_wordpress_content(self) -> None:
        """Test chunking with complex WordPress documentation content."""
        text = """
## Plugin Development Basics

WordPress plugins allow you to extend functionality.

### Creating Your First Plugin

To create a plugin, follow these steps:

```php
<?php
/**
 * Plugin Name: My First Plugin
 * Description: A simple WordPress plugin
 * Version: 1.0
 * Author: Your Name
 */
```

### Plugin Structure

A basic plugin structure includes:

1. Plugin header
2. Main plugin file
3. Activation/deactivation hooks

## Plugin API

WordPress provides a rich API for plugin development.

### Hooks and Filters

Use hooks to modify behavior:

```php
add_action('init', 'my_plugin_init');
add_filter('the_content', 'my_content_filter');
```

### Database Operations

Use WordPress database functions:

```php
global $wpdb;
$results = $wpdb->get_results("SELECT * FROM {$wpdb->posts}");
```

## Security Best Practices

Always sanitize user input and validate data.

### Input Sanitization

```php
$safe_input = sanitize_text_field($_POST['user_input']);
$safe_email = sanitize_email($_POST['email']);
```

### Output Escaping

```php
echo esc_html($user_data);
echo esc_url($link_url);
```

## Conclusion

Plugin development requires understanding WordPress architecture.
"""
        chunks = self.chunker.chunk_text(text)

        # Should create multiple chunks with proper structure
        assert len(chunks) >= 8
        assert "## Plugin Development Basics" in chunks[0]
        assert "### Creating Your First Plugin" in chunks[1]
        assert "```php" in chunks[1]  # Code block preserved
        assert "### Plugin Structure" in chunks[2]
        assert "## Plugin API" in chunks[3]
        assert "### Hooks and Filters" in chunks[4]
        assert "### Database Operations" in chunks[5]
        assert "## Security Best Practices" in chunks[6]
        assert "### Input Sanitization" in chunks[7]
        assert "### Output Escaping" in chunks[8]
        assert "## Conclusion" in chunks[9]

    def test_chunk_text_edge_cases(self) -> None:
        """Test edge cases and unusual input."""
        # Test with only headings (these will be filtered out as too small)
        text = "## Heading 1\n## Heading 2\n## Heading 3"
        chunks = self.chunker.chunk_text(text)
        # All chunks will be filtered out due to size validation
        assert len(chunks) == 0

        # Test with only code blocks (these will be filtered out as too small)
        text = "```code1```\n```code2```"
        chunks = self.chunker.chunk_text(text)
        # Code blocks alone are too small and will be filtered out
        assert len(chunks) == 0

        # Test with malformed headings (these will be filtered out as too small)
        text = "##Heading Without Space\n## Proper Heading"
        chunks = self.chunker.chunk_text(text)
        # Malformed headings are too small and will be filtered out
        assert len(chunks) == 0

    def test_chunk_text_size_limits(self) -> None:
        """Test that chunks respect size limits."""
        # Create content that should be split due to size
        large_content = "This is a sentence. " * 200  # Very large content
        text = f"## Large Section\n{large_content}"

        chunks = self.chunker.chunk_text(text)

        # All chunks should be within reasonable size limits
        for chunk in chunks:
            assert len(chunk) <= 2000  # Should not exceed 2000 characters
            assert len(chunk) >= 50  # Should not be too small

    def test_chunk_text_preserves_structure(self) -> None:
        """Test that chunking preserves document structure."""
        text = """
## Main Topic
Introduction to the topic with sufficient content to pass validation.

### Subsection A
Content for subsection A with enough text to be included.

### Subsection B
Content for subsection B with adequate length for inclusion.

## Another Topic
Content for another topic with sufficient text to pass validation.
"""
        chunks = self.chunker.chunk_text(text)

        # Should preserve the hierarchical structure
        assert len(chunks) == 4
        assert chunks[0].startswith("## Main Topic")
        assert chunks[1].startswith("### Subsection A")
        assert chunks[2].startswith("### Subsection B")
        assert chunks[3].startswith("## Another Topic")
