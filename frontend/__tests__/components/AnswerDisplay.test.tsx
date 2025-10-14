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

    const answerElement = screen.getByText(answerWithBreaks)
    expect(answerElement).toHaveClass('whitespace-pre-wrap')
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

    const section = screen.getByRole('region')
    expect(section).toHaveClass('space-y-3')

    const answerDiv = screen.getByText('Test answer').closest('div')
    expect(answerDiv).toHaveClass('rounded-md', 'border', 'border-gray-200', 'bg-white', 'p-4', 'whitespace-pre-wrap')

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
})
