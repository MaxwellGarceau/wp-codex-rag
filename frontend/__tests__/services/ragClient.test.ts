import { describe, it, expect, vi, beforeEach } from 'vitest'
import { RAGClient, RAGQueryResponse, ErrorProperties } from '@/services/ragClient'
import { HttpClient } from '@/services/httpClient'

// Mock HttpClient
vi.mock('@/services/httpClient')

describe('RAGClient', () => {
  let ragClient: RAGClient
  let mockHttpClient: any

  beforeEach(() => {
    vi.clearAllMocks()
    mockHttpClient = {
      post: vi.fn(),
    }
    vi.mocked(HttpClient).mockImplementation(() => mockHttpClient)
    ragClient = new RAGClient()
  })

  describe('constructor', () => {
    it('should create RAGClient with default base URL', () => {
      expect(HttpClient).toHaveBeenCalledWith(undefined)
      expect(ragClient).toBeInstanceOf(RAGClient)
    })

    it('should create RAGClient with custom base URL', () => {
      const customUrl = 'https://api.example.com'
      const client = new RAGClient(customUrl)
      expect(HttpClient).toHaveBeenCalledWith(customUrl)
      expect(client).toBeInstanceOf(RAGClient)
    })
  })

  describe('query method', () => {
    it('should make successful query and return response', async () => {
      const mockResponse: RAGQueryResponse = {
        answer: 'This is a test answer',
        sources: [
          { title: 'Test Source 1', url: 'https://example.com/1' },
          { title: 'Test Source 2', url: 'https://example.com/2' }
        ]
      }
      mockHttpClient.post.mockResolvedValueOnce(mockResponse)

      const result = await ragClient.query('What is WordPress?')

      expect(mockHttpClient.post).toHaveBeenCalledWith('/api/v1/rag/query', {
        question: 'What is WordPress?'
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle empty sources in response', async () => {
      const mockResponse: RAGQueryResponse = {
        answer: 'This is a test answer',
        sources: []
      }
      mockHttpClient.post.mockResolvedValueOnce(mockResponse)

      const result = await ragClient.query('What is WordPress?')

      expect(result).toEqual(mockResponse)
      expect(result.sources).toEqual([])
    })

    it('should handle missing sources in response', async () => {
      const mockResponse = {
        answer: 'This is a test answer'
        // sources property missing
      }
      mockHttpClient.post.mockResolvedValueOnce(mockResponse)

      const result = await ragClient.query('What is WordPress?')

      expect(result.answer).toBe('This is a test answer')
      expect(result.sources).toBeUndefined()
    })

    it('should handle HTTP client errors and re-throw them', async () => {
      const mockError = new Error('Network error')
      mockHttpClient.post.mockRejectedValueOnce(mockError)

      // Mock console.error to avoid noise in test output
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(ragClient.query('What is WordPress?')).rejects.toThrow('Network error')

      expect(consoleSpy).toHaveBeenCalledWith('RAG Client Error:', mockError)
      consoleSpy.mockRestore()
    })

    it('should handle structured error responses', async () => {
      const errorProperties: ErrorProperties = {
        message: 'Invalid question format',
        statusCode: 400,
        type: 'validation_error',
        providerCode: 'INVALID_INPUT'
      }
      const mockError = new Error(JSON.stringify(errorProperties))
      mockHttpClient.post.mockRejectedValueOnce(mockError)

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      await expect(ragClient.query('')).rejects.toThrow(JSON.stringify(errorProperties))

      expect(consoleSpy).toHaveBeenCalledWith('RAG Client Error:', mockError)
      consoleSpy.mockRestore()
    })

    it('should handle different question formats', async () => {
      const mockResponse: RAGQueryResponse = {
        answer: 'Test answer',
        sources: []
      }
      mockHttpClient.post.mockResolvedValue(mockResponse)

      // Test various question formats
      const questions = [
        'Simple question?',
        'Question with special characters: @#$%',
        'Question with numbers: 12345',
        'Very long question that might test the limits of the system and see how it handles longer input strings',
        ''
      ]

      for (const question of questions) {
        await ragClient.query(question)
        expect(mockHttpClient.post).toHaveBeenCalledWith('/api/v1/rag/query', {
          question
        })
      }
    })
  })
})
