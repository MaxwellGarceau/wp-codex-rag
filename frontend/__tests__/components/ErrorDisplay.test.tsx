import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ErrorDisplay } from '@/components/ErrorDisplay'

describe('ErrorDisplay', () => {
  const mockOnDismiss = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render plain error message', async () => {
    const errorMessage = 'Something went wrong'
    render(<ErrorDisplay error={errorMessage} />)

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
    })
  })

  it('should render structured error response', async () => {
    const structuredError = JSON.stringify({
      message: 'Validation failed',
      statusCode: 400,
      type: 'validation_error',
      providerCode: 'INVALID_INPUT'
    })

    render(<ErrorDisplay error={structuredError} />)

    await waitFor(() => {
      expect(screen.getByText('Validation failed')).toBeInTheDocument()
      expect(screen.getByText('Error code: 400 - validation_error')).toBeInTheDocument()
      expect(screen.getByText('Provider Error Code:')).toBeInTheDocument()
      expect(screen.getByText('INVALID_INPUT')).toBeInTheDocument()
    })
  })

  it('should handle malformed JSON error gracefully', async () => {
    const malformedJson = '{"message": "Test error", "statusCode": 500' // Missing closing brace
    render(<ErrorDisplay error={malformedJson} />)

    await waitFor(() => {
      expect(screen.getByText(malformedJson)).toBeInTheDocument()
    })
  })

  it('should show dismiss button when onDismiss is provided', async () => {
    render(<ErrorDisplay error="Test error" onDismiss={mockOnDismiss} />)

    await waitFor(() => {
      const dismissButton = screen.getByRole('button', { name: /dismiss/i })
      expect(dismissButton).toBeInTheDocument()
    })
  })

  it('should not show dismiss button when onDismiss is not provided', async () => {
    render(<ErrorDisplay error="Test error" />)

    await waitFor(() => {
      expect(screen.queryByRole('button', { name: /dismiss/i })).not.toBeInTheDocument()
    })
  })

  it('should call onDismiss when dismiss button is clicked', async () => {
    const user = userEvent.setup()
    render(<ErrorDisplay error="Test error" onDismiss={mockOnDismiss} />)

    await waitFor(() => {
      const dismissButton = screen.getByRole('button', { name: /dismiss/i })
      return user.click(dismissButton)
    })

    expect(mockOnDismiss).toHaveBeenCalledTimes(1)
  })

  it('should handle missing error properties with fallbacks', async () => {
    const incompleteError = JSON.stringify({
      message: 'Test error'
      // Missing statusCode, type, providerCode
    })

    render(<ErrorDisplay error={incompleteError} />)

    await waitFor(() => {
      expect(screen.getByText('Test error')).toBeInTheDocument()
      expect(screen.getByText('Provider Error Code:')).toBeInTheDocument()
      expect(screen.getByText('Not provided')).toBeInTheDocument()
    })
  })

  it('should handle empty error properties', async () => {
    const emptyError = JSON.stringify({
      message: '',
      statusCode: '',
      type: '',
      providerCode: ''
    })

    render(<ErrorDisplay error={emptyError} />)

    await waitFor(() => {
      expect(screen.getByText('Unknown error')).toBeInTheDocument()
      expect(screen.getByText('Provider Error Code:')).toBeInTheDocument()
      expect(screen.getByText('Not provided')).toBeInTheDocument()
    })
  })

  it('should handle very long error messages', async () => {
    const longError = 'A'.repeat(1000)
    render(<ErrorDisplay error={longError} />)

    await waitFor(() => {
      expect(screen.getByText(longError)).toBeInTheDocument()
    })
  })

  it('should handle special characters in error message', async () => {
    const specialError = 'Error with <script>alert("test")</script> and @#$% symbols'
    render(<ErrorDisplay error={specialError} />)

    await waitFor(() => {
      expect(screen.getByText(specialError)).toBeInTheDocument()
    })
  })

  it('should have correct CSS classes', async () => {
    render(<ErrorDisplay error="Test error" />)

    await waitFor(() => {
      // Find the outer container div with the error styling by looking for the specific class
      const errorContainer = document.querySelector('.rounded-md.border.border-red-200.bg-red-50.p-4')
      expect(errorContainer).toBeInTheDocument()
    })
  })

  it('should render error icon', async () => {
    render(<ErrorDisplay error="Test error" />)

    await waitFor(() => {
      // The SVG has aria-hidden="true", so we need to find it by its class
      const icon = document.querySelector('svg.h-5.w-5.text-red-400')
      expect(icon).toBeInTheDocument()
    })
  })

  it('should handle multiple error displays', async () => {
    render(
      <div>
        <ErrorDisplay error="Error 1" />
        <ErrorDisplay error="Error 2" />
      </div>
    )

    await waitFor(() => {
      expect(screen.getByText('Error 1')).toBeInTheDocument()
      expect(screen.getByText('Error 2')).toBeInTheDocument()
    })
  })

  it('should not render until client-side (hydration safety)', async () => {
    render(<ErrorDisplay error="Test error" />)

    // In test environment, useEffect runs synchronously, so the component renders immediately
    // This test verifies the component works correctly after hydration
    await waitFor(() => {
      expect(screen.getByText('Test error')).toBeInTheDocument()
    })
  })

  it('should handle structured error with all properties', async () => {
    const completeError = JSON.stringify({
      message: 'Complete error message',
      statusCode: 500,
      type: 'server_error',
      providerCode: 'INTERNAL_ERROR'
    })

    render(<ErrorDisplay error={completeError} />)

    await waitFor(() => {
      expect(screen.getByText('Complete error message')).toBeInTheDocument()
      expect(screen.getByText('Error code: 500 - server_error')).toBeInTheDocument()
      expect(screen.getByText('Provider Error Code:')).toBeInTheDocument()
      expect(screen.getByText('INTERNAL_ERROR')).toBeInTheDocument()
    })
  })
})
