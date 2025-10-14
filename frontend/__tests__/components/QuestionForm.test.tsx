import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QuestionForm } from '@/components/QuestionForm'

describe('QuestionForm', () => {
  const defaultProps = {
    question: '',
    loading: false,
    onQuestionChange: vi.fn(),
    onSubmit: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render textarea and button', () => {
    render(<QuestionForm {...defaultProps} />)

    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /ask/i })).toBeInTheDocument()
  })

  it('should display question value in textarea', () => {
    const question = 'What is WordPress?'
    render(<QuestionForm {...defaultProps} question={question} />)

    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveValue(question)
  })

  it('should call onQuestionChange when textarea value changes', async () => {
    const user = userEvent.setup()
    const onQuestionChange = vi.fn()

    render(<QuestionForm {...defaultProps} onQuestionChange={onQuestionChange} />)

    const textarea = screen.getByRole('textbox')
    await user.type(textarea, 'New question')

    // user.type() calls onChange for each character, so we check that it was called
    expect(onQuestionChange).toHaveBeenCalledTimes(12) // One for each character
    // Check that it was called with individual characters
    expect(onQuestionChange).toHaveBeenNthCalledWith(1, 'N')
    expect(onQuestionChange).toHaveBeenNthCalledWith(12, 'n')
    // The textarea value doesn't change because it's controlled by the parent component
    // The parent would need to update the question prop for the value to change
  })

  it('should call onSubmit when button is clicked', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()

    render(<QuestionForm {...defaultProps} question="Test question" onSubmit={onSubmit} />)

    const button = screen.getByRole('button', { name: /ask/i })
    await user.click(button)

    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  it('should disable button when loading', () => {
    render(<QuestionForm {...defaultProps} loading={true} />)

    const button = screen.getByRole('button', { name: /thinking/i })
    expect(button).toBeDisabled()
  })

  it('should disable button when question is empty', () => {
    render(<QuestionForm {...defaultProps} question="" />)

    const button = screen.getByRole('button', { name: /ask/i })
    expect(button).toBeDisabled()
  })

  it('should disable button when question is only whitespace', () => {
    render(<QuestionForm {...defaultProps} question="   " />)

    const button = screen.getByRole('button', { name: /ask/i })
    expect(button).toBeDisabled()
  })

  it('should enable button when question has content and not loading', () => {
    render(<QuestionForm {...defaultProps} question="Valid question" loading={false} />)

    const button = screen.getByRole('button', { name: /ask/i })
    expect(button).not.toBeDisabled()
  })

  it('should show "Thinking..." text when loading', () => {
    render(<QuestionForm {...defaultProps} loading={true} />)

    expect(screen.getByText('Thinking…')).toBeInTheDocument()
  })

  it('should show "Ask" text when not loading', () => {
    render(<QuestionForm {...defaultProps} loading={false} question="Test" />)

    expect(screen.getByText('Ask')).toBeInTheDocument()
  })

  it('should have correct placeholder text', () => {
    render(<QuestionForm {...defaultProps} />)

    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('placeholder', 'e.g. How do I register a custom post type in a plugin?')
  })

  it('should have correct CSS classes', () => {
    render(<QuestionForm {...defaultProps} />)

    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveClass('w-full', 'min-h-[120px]', 'rounded-md', 'border', 'border-gray-300', 'p-3')

    const button = screen.getByRole('button')
    expect(button).toHaveClass('inline-flex', 'items-center', 'rounded-md', 'bg-blue-600', 'px-4', 'py-2', 'text-white')
  })

  it('should handle Enter key in textarea', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()

    render(<QuestionForm {...defaultProps} question="Test question" onSubmit={onSubmit} />)

    const textarea = screen.getByRole('textbox')
    await user.type(textarea, '{enter}')

    // Note: The component doesn't handle Enter key submission, so this test verifies current behavior
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('should handle rapid typing', async () => {
    const user = userEvent.setup()
    const onQuestionChange = vi.fn()

    render(<QuestionForm {...defaultProps} onQuestionChange={onQuestionChange} />)

    const textarea = screen.getByRole('textbox')
    await user.type(textarea, 'Hello World')

    expect(onQuestionChange).toHaveBeenCalledTimes(11) // One for each character
  })
})
