import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { RAGToggle } from '../RAGToggle';

describe('RAGToggle', () => {
  const mockOnToggle = vi.fn();

  beforeEach(() => {
    mockOnToggle.mockClear();
  });

  describe('Rendering', () => {
    it('renders with RAG enabled by default', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);

      expect(screen.getByText('With RAG')).toBeInTheDocument();
      expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'true');
    });

    it('renders with RAG disabled', () => {
      render(<RAGToggle useRAG={false} onToggle={mockOnToggle} />);

      expect(screen.getByText('Without RAG')).toBeInTheDocument();
      expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'false');
    });

    it('renders with correct accessibility attributes', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);

      const switchElement = screen.getByRole('switch');
      expect(switchElement).toHaveAttribute('aria-checked', 'true');
      expect(switchElement).toHaveAttribute('aria-label', 'Toggle off RAG');
    });

    it('renders with correct accessibility attributes when RAG is off', () => {
      render(<RAGToggle useRAG={false} onToggle={mockOnToggle} />);

      const switchElement = screen.getByRole('switch');
      expect(switchElement).toHaveAttribute('aria-checked', 'false');
      expect(switchElement).toHaveAttribute('aria-label', 'Toggle on RAG');
    });
  });

  describe('Toggle Functionality', () => {
    it('calls onToggle with opposite value when clicked', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);

      const toggleButton = screen.getByRole('switch');
      fireEvent.click(toggleButton);

      expect(mockOnToggle).toHaveBeenCalledTimes(1);
      expect(mockOnToggle).toHaveBeenCalledWith(false);
    });

    it('calls onToggle with true when RAG is off and clicked', () => {
      render(<RAGToggle useRAG={false} onToggle={mockOnToggle} />);

      const toggleButton = screen.getByRole('switch');
      fireEvent.click(toggleButton);

      expect(mockOnToggle).toHaveBeenCalledTimes(1);
      expect(mockOnToggle).toHaveBeenCalledWith(true);
    });

    it('does not call onToggle when disabled and clicked', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} disabled={true} />);

      const toggleButton = screen.getByRole('switch');
      fireEvent.click(toggleButton);

      expect(mockOnToggle).not.toHaveBeenCalled();
    });
  });

  describe('Disabled State', () => {
    it('applies disabled styling when disabled prop is true', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} disabled={true} />);

      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).toBeDisabled();
      expect(toggleButton).toHaveClass('opacity-50', 'cursor-not-allowed');
    });

    it('applies disabled text styling when disabled', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} disabled={true} />);

      const textElement = screen.getByText('With RAG');
      expect(textElement).toHaveClass('text-gray-400');
    });

    it('applies normal styling when not disabled', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} disabled={false} />);

      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).not.toHaveClass('opacity-50', 'cursor-not-allowed');
      expect(toggleButton).toHaveClass('cursor-pointer');
    });

    it('applies normal text styling when not disabled', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} disabled={false} />);

      const textElement = screen.getByText('With RAG');
      expect(textElement).toHaveClass('text-gray-700');
    });
  });

  describe('Visual States', () => {
    it('applies correct classes when RAG is enabled', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);

      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).toHaveClass('bg-blue-600');

      const slider = toggleButton.querySelector('span');
      expect(slider).toHaveClass('translate-x-6');
    });

    it('applies correct classes when RAG is disabled', () => {
      render(<RAGToggle useRAG={false} onToggle={mockOnToggle} />);

      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).toHaveClass('bg-gray-200');

      const slider = toggleButton.querySelector('span');
      expect(slider).toHaveClass('translate-x-1');
    });

    it('shows correct text based on RAG state', () => {
      const { rerender } = render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);
      expect(screen.getByText('With RAG')).toBeInTheDocument();
      expect(screen.queryByText('Without RAG')).not.toBeInTheDocument();

      rerender(<RAGToggle useRAG={false} onToggle={mockOnToggle} />);
      expect(screen.getByText('Without RAG')).toBeInTheDocument();
      expect(screen.queryByText('With RAG')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper role attribute', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);

      expect(screen.getByRole('switch')).toBeInTheDocument();
    });

    it('has proper aria-checked attribute', () => {
      const { rerender } = render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);
      expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'true');

      rerender(<RAGToggle useRAG={false} onToggle={mockOnToggle} />);
      expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'false');
    });

    it('has descriptive aria-label', () => {
      const { rerender } = render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);
      expect(screen.getByRole('switch')).toHaveAttribute('aria-label', 'Toggle off RAG');

      rerender(<RAGToggle useRAG={false} onToggle={mockOnToggle} />);
      expect(screen.getByRole('switch')).toHaveAttribute('aria-label', 'Toggle on RAG');
    });

    it('is keyboard accessible', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);

      const toggleButton = screen.getByRole('switch');
      toggleButton.focus();
      expect(toggleButton).toHaveFocus();
    });
  });

  describe('Edge Cases', () => {
    it('handles rapid clicking', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);

      const toggleButton = screen.getByRole('switch');

      // Click multiple times rapidly
      fireEvent.click(toggleButton);
      fireEvent.click(toggleButton);
      fireEvent.click(toggleButton);

      // Should call onToggle for each click with the opposite value
      expect(mockOnToggle).toHaveBeenCalledTimes(3);
      expect(mockOnToggle).toHaveBeenNthCalledWith(1, false);
      expect(mockOnToggle).toHaveBeenNthCalledWith(2, false);
      expect(mockOnToggle).toHaveBeenNthCalledWith(3, false);
    });

    it('handles undefined disabled prop', () => {
      render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);

      const toggleButton = screen.getByRole('switch');
      expect(toggleButton).not.toBeDisabled();
      expect(toggleButton).toHaveClass('cursor-pointer');
    });

    it('maintains state consistency during re-renders', () => {
      const { rerender } = render(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);

      // Re-render with same props
      rerender(<RAGToggle useRAG={true} onToggle={mockOnToggle} />);

      expect(screen.getByText('With RAG')).toBeInTheDocument();
      expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'true');
    });
  });
});
