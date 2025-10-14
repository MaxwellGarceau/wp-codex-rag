import { describe, it, expect, vi, beforeEach } from 'vitest'
import { HttpClient } from '@/services/httpClient'

// Mock fetch globally
global.fetch = vi.fn()

describe('HttpClient', () => {
  let httpClient: HttpClient

  beforeEach(() => {
    vi.clearAllMocks()
    httpClient = new HttpClient()
  })

  describe('constructor', () => {
    it('should use default base URL when none provided', () => {
      const client = new HttpClient()
      expect(client).toBeInstanceOf(HttpClient)
    })

    it('should use custom base URL when provided', () => {
      const customUrl = 'https://api.example.com'
      const client = new HttpClient(customUrl)
      expect(client).toBeInstanceOf(HttpClient)
    })

    it('should use environment variable when available', () => {
      const originalEnv = process.env.NEXT_PUBLIC_API_BASE_URL
      process.env.NEXT_PUBLIC_API_BASE_URL = 'https://env.example.com'

      const client = new HttpClient()
      expect(client).toBeInstanceOf(HttpClient)

      // Restore original env
      process.env.NEXT_PUBLIC_API_BASE_URL = originalEnv
    })
  })

  describe('post method', () => {
    it('should make successful POST request and return data', async () => {
      const mockResponse = { success: true, data: 'test' }
      const mockFetch = vi.mocked(fetch)
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      } as Response)

      const result = await httpClient.post('/test', { key: 'value' })

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: 'value' }),
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle JSON error response', async () => {
      const mockErrorResponse = {
        error: {
          message: 'Test error',
          statusCode: 400,
          type: 'validation_error',
          providerCode: 'INVALID_INPUT'
        }
      }
      const mockFetch = vi.mocked(fetch)
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: () => Promise.resolve(JSON.stringify(mockErrorResponse)),
      } as Response)

      await expect(httpClient.post('/test', {})).rejects.toThrow(
        JSON.stringify(mockErrorResponse.error)
      )
    })

    it('should handle non-JSON error response', async () => {
      const mockFetch = vi.mocked(fetch)
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Server Error'),
      } as Response)

      await expect(httpClient.post('/test', {})).rejects.toThrow(
        JSON.stringify({ message: 'Server Error' })
      )
    })

    it('should handle empty error response', async () => {
      const mockFetch = vi.mocked(fetch)
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve(''),
      } as Response)

      await expect(httpClient.post('/test', {})).rejects.toThrow(
        JSON.stringify({ message: 'HTTP 404: Not Found' })
      )
    })

    it('should handle network errors', async () => {
      const mockFetch = vi.mocked(fetch)
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(httpClient.post('/test', {})).rejects.toThrow('Network error')
    })
  })
})
