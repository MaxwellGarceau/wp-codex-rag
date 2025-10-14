import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import HomePage from '@/page'
import { RAGClient } from '@/services/ragClient'

// Mock the RAGClient
vi.mock('@/services/ragClient')

describe('HomePage', () => {
  let mockRAGClient: any

  beforeEach(() => {
    vi.clearAllMocks()
    mockRAGClient = {
      query: vi.fn(),
    }
    vi.mocked(RAGClient).mockImplementation(() => mockRAGClient)
  })

  it('should render the main page structure', () => {
    render(<HomePage />)

    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('WordPress Codex Q&A')
    expect(screen.getByText('Ask questions about plugin development.')).toBeInTheDocument()
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /ask/i })).toBeInTheDocument()
  })

  it('should handle successful query', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      answer: 'WordPress is a content management system.',
      sources: [
        { title: 'WordPress.org', url: 'https://wordpress.org' }
      ]
    }
    mockRAGClient.query.mockResolvedValueOnce(mockResponse)

    render(<HomePage />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /ask/i })

    await user.type(textarea, 'What is WordPress?')
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('WordPress is a content management system.')).toBeInTheDocument()
      expect(screen.getByText('WordPress.org')).toBeInTheDocument()
    })
  })

  it('should handle query error', async () => {
    const user = userEvent.setup()
    const mockError = new Error('Network error')
    mockRAGClient.query.mockRejectedValueOnce(mockError)

    render(<HomePage />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /ask/i })

    await user.type(textarea, 'Test question')
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument()
    })
  })

  it('should handle query error with message property', async () => {
    const user = userEvent.setup()
    const mockError = { message: 'Custom error message' }
    mockRAGClient.query.mockRejectedValueOnce(mockError)

    render(<HomePage />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /ask/i })

    await user.type(textarea, 'Test question')
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('Custom error message')).toBeInTheDocument()
    })
  })

  it('should handle query error without message property', async () => {
    const user = userEvent.setup()
    const mockError = new Error()
    mockRAGClient.query.mockRejectedValueOnce(mockError)

    render(<HomePage />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /ask/i })

    await user.type(textarea, 'Test question')
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('Request failed')).toBeInTheDocument()
    })
  })

  it('should show loading state during query', async () => {
    const user = userEvent.setup()
    // Create a promise that we can control
    let resolveQuery: (value: any) => void
    const queryPromise = new Promise((resolve) => {
      resolveQuery = resolve
    })
    mockRAGClient.query.mockReturnValueOnce(queryPromise)

    render(<HomePage />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /ask/i })

    await user.type(textarea, 'Test question')
    await user.click(button)

    // Should show loading state
    expect(screen.getByText('Thinking…')).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeDisabled()

    // Resolve the query
    resolveQuery!({
      answer: 'Test answer',
      sources: []
    })

    await waitFor(() => {
      expect(screen.getByText('Test answer')).toBeInTheDocument()
    })
  })

  it('should clear previous results when starting new query', async () => {
    const user = userEvent.setup()
    const firstResponse = {
      answer: 'First answer',
      sources: [{ title: 'First source', url: 'https://example.com/1' }]
    }
    const secondResponse = {
      answer: 'Second answer',
      sources: [{ title: 'Second source', url: 'https://example.com/2' }]
    }

    mockRAGClient.query
      .mockResolvedValueOnce(firstResponse)
      .mockResolvedValueOnce(secondResponse)

    render(<HomePage />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /ask/i })

    // First query
    await user.type(textarea, 'First question')
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('First answer')).toBeInTheDocument()
      expect(screen.getByText('First source')).toBeInTheDocument()
    })

    // Clear textarea and start second query
    await user.clear(textarea)
    await user.type(textarea, 'Second question')
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('Second answer')).toBeInTheDocument()
      expect(screen.getByText('Second source')).toBeInTheDocument()
      // Previous results should be cleared
      expect(screen.queryByText('First answer')).not.toBeInTheDocument()
      expect(screen.queryByText('First source')).not.toBeInTheDocument()
    })
  })

  it('should handle empty sources in response', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      answer: 'Answer without sources',
      sources: []
    }
    mockRAGClient.query.mockResolvedValueOnce(mockResponse)

    render(<HomePage />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /ask/i })

    await user.type(textarea, 'Test question')
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('Answer without sources')).toBeInTheDocument()
      expect(screen.queryByText('Sources')).not.toBeInTheDocument()
    })
  })

  it('should handle missing sources in response', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      answer: 'Answer without sources property'
      // sources property missing
    }
    mockRAGClient.query.mockResolvedValueOnce(mockResponse)

    render(<HomePage />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /ask/i })

    await user.type(textarea, 'Test question')
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('Answer without sources property')).toBeInTheDocument()
      expect(screen.queryByText('Sources')).not.toBeInTheDocument()
    })
  })

  it('should disable button when question is empty', () => {
    render(<HomePage />)

    const button = screen.getByRole('button', { name: /ask/i })
    expect(button).toBeDisabled()
  })

  it('should enable button when question has content', async () => {
    const user = userEvent.setup()
    render(<HomePage />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /ask/i })

    await user.type(textarea, 'Test question')

    expect(button).not.toBeDisabled()
  })

  it('should dismiss error when dismiss button is clicked', async () => {
    const user = userEvent.setup()
    const mockError = new Error('Test error')
    mockRAGClient.query.mockRejectedValueOnce(mockError)

    render(<HomePage />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /ask/i })

    await user.type(textarea, 'Test question')
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText('Test error')).toBeInTheDocument()
    })

    const dismissButton = screen.getByRole('button', { name: /dismiss/i })
    await user.click(dismissButton)

    expect(screen.queryByText('Test error')).not.toBeInTheDocument()
  })
})
