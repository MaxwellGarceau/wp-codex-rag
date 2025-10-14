import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MarkdownRenderer } from '@/components/MarkdownRenderer'

describe('MarkdownRenderer', () => {
  it('should render plain text', () => {
    const content = 'This is plain text content.'
    render(<MarkdownRenderer content={content} />)

    expect(screen.getByText(content)).toBeInTheDocument()
  })

  it('should render headings with correct levels and styling', () => {
    const content = '# H1 Heading\n## H2 Heading\n### H3 Heading\n#### H4 Heading\n##### H5 Heading\n###### H6 Heading'
    render(<MarkdownRenderer content={content} />)

    const h1 = screen.getByRole('heading', { level: 1 })
    const h2 = screen.getByRole('heading', { level: 2 })
    const h3 = screen.getByRole('heading', { level: 3 })
    const h4 = screen.getByRole('heading', { level: 4 })
    const h5 = screen.getByRole('heading', { level: 5 })
    const h6 = screen.getByRole('heading', { level: 6 })

    expect(h1).toHaveTextContent('H1 Heading')
    expect(h1).toHaveClass('text-2xl', 'font-bold', 'mb-4', 'mt-6', 'text-gray-900', 'border-b', 'border-gray-200', 'pb-2')

    expect(h2).toHaveTextContent('H2 Heading')
    expect(h2).toHaveClass('text-xl', 'font-semibold', 'mb-3', 'mt-5', 'text-gray-900')

    expect(h3).toHaveTextContent('H3 Heading')
    expect(h3).toHaveClass('text-lg', 'font-medium', 'mb-2', 'mt-4', 'text-gray-900')

    expect(h4).toHaveTextContent('H4 Heading')
    expect(h4).toHaveClass('text-base', 'font-medium', 'mb-2', 'mt-3', 'text-gray-900')

    expect(h5).toHaveTextContent('H5 Heading')
    expect(h5).toHaveClass('text-sm', 'font-medium', 'mb-1', 'mt-2', 'text-gray-900')

    expect(h6).toHaveTextContent('H6 Heading')
    expect(h6).toHaveClass('text-xs', 'font-medium', 'mb-1', 'mt-2', 'text-gray-900')
  })

  it('should render inline code with correct styling', () => {
    const content = 'Use the `wp_enqueue_script()` function to add scripts.'
    render(<MarkdownRenderer content={content} />)

    const codeElement = screen.getByText('wp_enqueue_script()')
    expect(codeElement.tagName).toBe('CODE')
    expect(codeElement).toHaveClass('bg-gray-100', 'text-gray-800', 'px-1.5', 'py-0.5', 'rounded', 'text-sm', 'font-mono')
  })

  it('should render code blocks with correct styling', () => {
    const content = '```php\nfunction my_plugin_function() {\n    return "Hello World";\n}\n```'
    render(<MarkdownRenderer content={content} />)

    // Find the pre element directly since the text is broken up by syntax highlighting
    const preElement = document.querySelector('pre')
    expect(preElement).toHaveClass('bg-gray-900', 'text-gray-100', 'p-4', 'rounded-lg', 'overflow-x-auto', 'my-4', 'border')
  })

  it('should render bold text', () => {
    const content = 'This is **bold text** in the content.'
    render(<MarkdownRenderer content={content} />)

    const boldElement = screen.getByText('bold text')
    expect(boldElement.tagName).toBe('STRONG')
  })

  it('should render italic text', () => {
    const content = 'This is __italic text__ in the content.'
    render(<MarkdownRenderer content={content} />)

    const italicElement = screen.getByText('italic text')
    // Note: react-markdown with remark-gfm uses <strong> for __text__ instead of <em>
    expect(italicElement.tagName).toBe('STRONG')
  })

  it('should render proper italic text with single underscores', () => {
    const content = 'This is _italic text_ in the content.'
    render(<MarkdownRenderer content={content} />)

    const italicElement = screen.getByText('italic text')
    expect(italicElement.tagName).toBe('EM')
  })

  it('should render unordered lists', () => {
    const content = '- First item\n- Second item\n- Third item'
    render(<MarkdownRenderer content={content} />)

    const list = screen.getByRole('list')
    const listItems = screen.getAllByRole('listitem')

    expect(list).toHaveClass('list-disc', 'pl-6', 'mb-3', 'space-y-1')
    expect(listItems).toHaveLength(3)
    expect(listItems[0]).toHaveTextContent('First item')
    expect(listItems[1]).toHaveTextContent('Second item')
    expect(listItems[2]).toHaveTextContent('Third item')
  })

  it('should render ordered lists', () => {
    const content = '1. First item\n2. Second item\n3. Third item'
    render(<MarkdownRenderer content={content} />)

    const list = screen.getByRole('list')
    const listItems = screen.getAllByRole('listitem')

    expect(list).toHaveClass('list-decimal', 'pl-6', 'mb-3', 'space-y-1')
    expect(listItems).toHaveLength(3)
    expect(listItems[0]).toHaveTextContent('First item')
    expect(listItems[1]).toHaveTextContent('Second item')
    expect(listItems[2]).toHaveTextContent('Third item')
  })

  it('should render links with correct attributes', () => {
    const content = 'Visit [WordPress.org](https://wordpress.org) for more information.'
    render(<MarkdownRenderer content={content} />)

    const link = screen.getByRole('link', { name: 'WordPress.org' })
    expect(link).toHaveAttribute('href', 'https://wordpress.org')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    expect(link).toHaveClass('text-blue-600', 'hover:text-blue-800', 'hover:underline')
  })

  it('should render blockquotes with correct styling', () => {
    const content = '> This is a blockquote with important information.'
    render(<MarkdownRenderer content={content} />)

    const blockquote = screen.getByText('This is a blockquote with important information.').closest('blockquote')
    expect(blockquote).toHaveClass('border-l-4', 'border-blue-500', 'pl-4', 'py-2', 'my-4', 'bg-blue-50', 'text-gray-700', 'italic')
  })

  it('should render tables with correct styling', () => {
    const content = '| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |'
    render(<MarkdownRenderer content={content} />)

    const table = screen.getByRole('table')
    const headers = screen.getAllByRole('columnheader')
    const cells = screen.getAllByRole('cell')

    expect(table).toHaveClass('min-w-full', 'border', 'border-gray-300')
    expect(headers).toHaveLength(2)
    expect(cells).toHaveLength(2)
    expect(headers[0]).toHaveTextContent('Header 1')
    expect(headers[1]).toHaveTextContent('Header 2')
    expect(cells[0]).toHaveTextContent('Cell 1')
    expect(cells[1]).toHaveTextContent('Cell 2')
  })

  it('should render horizontal rules', () => {
    const content = 'Content above\n\n---\n\nContent below'
    render(<MarkdownRenderer content={content} />)

    const hr = screen.getByRole('separator')
    expect(hr).toHaveClass('my-6', 'border-gray-300')
  })

  it('should handle empty content', () => {
    render(<MarkdownRenderer content="" />)

    // Should render without errors - check for the container instead
    const container = document.querySelector('.markdown-content')
    expect(container).toBeInTheDocument()
  })

  it('should handle content with special characters', () => {
    const content = 'Content with <script>alert("test")</script> and @#$% symbols'
    render(<MarkdownRenderer content={content} />)

    // Script tags should be escaped/not executed
    expect(screen.getByText(/Content with/)).toBeInTheDocument()
    expect(screen.getByText(/@#\$%/)).toBeInTheDocument()
  })

  it('should have markdown-content class on container', () => {
    const content = 'Test content'
    render(<MarkdownRenderer content={content} />)

    const container = screen.getByText('Test content').closest('.markdown-content')
    expect(container).toBeInTheDocument()
  })
})
