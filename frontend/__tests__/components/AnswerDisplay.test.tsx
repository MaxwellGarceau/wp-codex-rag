import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AnswerDisplay } from '@/components/AnswerDisplay'
import { RAGSource } from '@/services/ragClient'

describe('AnswerDisplay', () => {
  const mockSources: RAGSource[] = [
    { title: 'WordPress Plugin Development', url: 'https://example.com/plugin-dev' },
    { title: 'Custom Post Types', url: 'https://example.com/custom-posts' },
    { title: 'WordPress Hooks', url: 'https://example.com/hooks' }
  ]

  it('should render answer text', () => {
    const answer = 'This is a test answer about WordPress development.'
    render(<AnswerDisplay answer={answer} sources={[]} />)

    expect(screen.getByText(answer)).toBeInTheDocument()
  })

  it('should render answer heading', () => {
    render(<AnswerDisplay answer="Test answer" sources={[]} />)

    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Answer')
  })

  it('should render sources when provided', () => {
    const answer = 'Test answer'
    render(<AnswerDisplay answer={answer} sources={mockSources} />)

    expect(screen.getByText('Sources')).toBeInTheDocument()
    expect(screen.getByText('WordPress Plugin Development')).toBeInTheDocument()
    expect(screen.getByText('Custom Post Types')).toBeInTheDocument()
    expect(screen.getByText('WordPress Hooks')).toBeInTheDocument()
  })

  it('should not render sources section when sources array is empty', () => {
    render(<AnswerDisplay answer="Test answer" sources={[]} />)

    expect(screen.queryByText('Sources')).not.toBeInTheDocument()
  })

  it('should render source links with correct attributes', () => {
    render(<AnswerDisplay answer="Test answer" sources={mockSources} />)

    const links = screen.getAllByRole('link')
    expect(links).toHaveLength(3)

    links.forEach((link, index) => {
      expect(link).toHaveAttribute('href', mockSources[index].url)
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noreferrer')
    })
  })

  it('should handle single source', () => {
    const singleSource = [mockSources[0]]
    render(<AnswerDisplay answer="Test answer" sources={singleSource} />)

    expect(screen.getByText('Sources')).toBeInTheDocument()
    expect(screen.getByText('WordPress Plugin Development')).toBeInTheDocument()
    expect(screen.getAllByRole('link')).toHaveLength(1)
  })

  it('should handle answer with line breaks', () => {
    const answerWithBreaks = 'Line 1\nLine 2\nLine 3'
    render(<AnswerDisplay answer={answerWithBreaks} sources={[]} />)

    // Check that the answer is rendered (the text might be normalized by markdown)
    expect(screen.getByText(/Line 1/)).toBeInTheDocument()
    expect(screen.getByText(/Line 2/)).toBeInTheDocument()
    expect(screen.getByText(/Line 3/)).toBeInTheDocument()

    // Check that the outer container has the correct class
    const outerContainer = screen.getByText(/Line 1/).closest('div')?.parentElement
    expect(outerContainer).toHaveClass('rounded-md', 'border', 'border-gray-200', 'bg-white', 'p-4')
  })

  it('should handle special characters in answer', () => {
    const specialAnswer = 'Answer with <script>alert("test")</script> and @#$% symbols'
    render(<AnswerDisplay answer={specialAnswer} sources={[]} />)

    expect(screen.getByText(specialAnswer)).toBeInTheDocument()
  })

  it('should handle special characters in source titles', () => {
    const specialSources: RAGSource[] = [
      { title: 'Title with <script>alert("test")</script>', url: 'https://example.com/1' },
      { title: 'Title with @#$% symbols', url: 'https://example.com/2' }
    ]

    render(<AnswerDisplay answer="Test answer" sources={specialSources} />)

    expect(screen.getByText('Title with <script>alert("test")</script>')).toBeInTheDocument()
    expect(screen.getByText('Title with @#$% symbols')).toBeInTheDocument()
  })

  it('should handle very long answer', () => {
    const longAnswer = 'A'.repeat(1000)
    render(<AnswerDisplay answer={longAnswer} sources={[]} />)

    expect(screen.getByText(longAnswer)).toBeInTheDocument()
  })

  it('should handle many sources', () => {
    const manySources: RAGSource[] = Array.from({ length: 20 }, (_, i) => ({
      title: `Source ${i + 1}`,
      url: `https://example.com/${i + 1}`
    }))

    render(<AnswerDisplay answer="Test answer" sources={manySources} />)

    expect(screen.getByText('Sources')).toBeInTheDocument()
    expect(screen.getAllByRole('link')).toHaveLength(20)
  })

  it('should have correct CSS classes', () => {
    render(<AnswerDisplay answer="Test answer" sources={mockSources} />)

    // Find the section element (it doesn't have a region role)
    const section = screen.getByText('Answer').closest('section')
    expect(section).toHaveClass('space-y-3')

    const answerDiv = screen.getByText('Test answer').closest('div')?.parentElement
    expect(answerDiv).toHaveClass('rounded-md', 'border', 'border-gray-200', 'bg-white', 'p-4')

    const sourcesHeading = screen.getByText('Sources')
    expect(sourcesHeading).toHaveClass('font-medium')
  })

  it('should generate unique keys for sources', () => {
    const duplicateUrlSources: RAGSource[] = [
      { title: 'Source 1', url: 'https://example.com/same' },
      { title: 'Source 2', url: 'https://example.com/same' }
    ]

    render(<AnswerDisplay answer="Test answer" sources={duplicateUrlSources} />)

    // Should render both sources even with duplicate URLs
    expect(screen.getByText('Source 1')).toBeInTheDocument()
    expect(screen.getByText('Source 2')).toBeInTheDocument()
    expect(screen.getAllByRole('link')).toHaveLength(2)
  })

  // Tests for markdown rendering functionality
  it('should render markdown headings', () => {
    const markdownAnswer = '# Main Heading\n## Sub Heading\n### Small Heading'
    render(<AnswerDisplay answer={markdownAnswer} sources={[]} />)

    // Use getAllByRole since there are multiple h2 elements (Answer heading + Sub Heading)
    const h1Elements = screen.getAllByRole('heading', { level: 1 })
    const h2Elements = screen.getAllByRole('heading', { level: 2 })
    const h3Elements = screen.getAllByRole('heading', { level: 3 })

    expect(h1Elements).toHaveLength(1)
    expect(h1Elements[0]).toHaveTextContent('Main Heading')
    expect(h2Elements).toHaveLength(2) // Answer heading + Sub Heading
    expect(h2Elements[1]).toHaveTextContent('Sub Heading')
    expect(h3Elements).toHaveLength(1)
    expect(h3Elements[0]).toHaveTextContent('Small Heading')
  })

  it('should render inline code', () => {
    const codeAnswer = 'Use the `wp_enqueue_script()` function to add scripts.'
    render(<AnswerDisplay answer={codeAnswer} sources={[]} />)

    const codeElement = screen.getByText('wp_enqueue_script()')
    expect(codeElement.tagName).toBe('CODE')
    expect(codeElement).toHaveClass('bg-gray-100', 'text-gray-800', 'px-1.5', 'py-0.5', 'rounded', 'text-sm', 'font-mono')
  })

  it('should render code blocks', () => {
    const codeBlockAnswer = '```php\nfunction my_plugin_function() {\n    return "Hello World";\n}\n```'
    render(<AnswerDisplay answer={codeBlockAnswer} sources={[]} />)

    // Find the pre element directly since the text is broken up by syntax highlighting
    const preElement = document.querySelector('pre')
    expect(preElement).toHaveClass('bg-gray-900', 'text-gray-100', 'p-4', 'rounded-lg', 'overflow-x-auto', 'my-4', 'border')
  })

  it('should render bold and italic text', () => {
    const formattedAnswer = 'This is **bold text** and this is __italic text__.'
    render(<AnswerDisplay answer={formattedAnswer} sources={[]} />)

    expect(screen.getByText('bold text')).toBeInTheDocument()
    expect(screen.getByText('italic text')).toBeInTheDocument()
  })

  it('should render lists', () => {
    const listAnswer = '- First item\n- Second item\n- Third item'
    render(<AnswerDisplay answer={listAnswer} sources={[]} />)

    const listItems = screen.getAllByRole('listitem')
    expect(listItems).toHaveLength(3)
    expect(listItems[0]).toHaveTextContent('First item')
    expect(listItems[1]).toHaveTextContent('Second item')
    expect(listItems[2]).toHaveTextContent('Third item')
  })

  it('should render links', () => {
    const linkAnswer = 'Visit [WordPress.org](https://wordpress.org) for more information.'
    render(<AnswerDisplay answer={linkAnswer} sources={[]} />)

    const link = screen.getByRole('link', { name: 'WordPress.org' })
    expect(link).toHaveAttribute('href', 'https://wordpress.org')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })
})
