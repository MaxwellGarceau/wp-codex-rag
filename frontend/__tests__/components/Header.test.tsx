import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Header } from '@/components/Header'

describe('Header', () => {
  it('should render title and description', () => {
    const title = 'Test Title'
    const description = 'Test Description'

    render(<Header title={title} description={description} />)

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(title)
    expect(screen.getByText(description)).toBeInTheDocument()
  })

  it('should render with different title and description', () => {
    const title = 'WordPress Codex Q&A'
    const description = 'Ask questions about plugin development.'

    render(<Header title={title} description={description} />)

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(title)
    expect(screen.getByText(description)).toBeInTheDocument()
  })

  it('should have correct CSS classes', () => {
    render(<Header title="Test" description="Test" />)

    const header = screen.getByRole('banner')
    expect(header).toHaveClass('space-y-1')

    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toHaveClass('text-3xl', 'font-semibold')

    const description = screen.getByText('Test')
    expect(description).toHaveClass('text-gray-600')
  })

  it('should handle empty strings', () => {
    render(<Header title="" description="" />)

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('')
    expect(screen.getByText('')).toBeInTheDocument()
  })

  it('should handle special characters in title and description', () => {
    const title = 'Title with @#$% special chars'
    const description = 'Description with <script>alert("test")</script>'

    render(<Header title={title} description={description} />)

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(title)
    expect(screen.getByText(description)).toBeInTheDocument()
  })
})
