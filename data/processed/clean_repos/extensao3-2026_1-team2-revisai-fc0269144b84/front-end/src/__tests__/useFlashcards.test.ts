import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useFlashcards } from '../hooks/useFlashcards'

vi.mock('../services/flashcard.service', () => ({
  generateFlashcards: vi.fn(),
  ApiError: class ApiError extends Error {
    statusCode: number
    constructor(statusCode: number, message: string) {
      super(message)
      this.statusCode = statusCode
      this.name = 'ApiError'
    }
  },
  NetworkError: class NetworkError extends Error {
    constructor() {
      super('Falha de conexão.')
      this.name = 'NetworkError'
    }
  },
}))

import * as service from '../services/flashcard.service'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('useFlashcards hook', () => {
  it('initial state is idle with null artifact', () => {
    const { result } = renderHook(() => useFlashcards())
    expect(result.current.status).toBe('idle')
    expect(result.current.artifact).toBeNull()
    expect(result.current.errorMessage).toBeNull()
  })

  it('sets error when content and file are both empty', async () => {
    const { result } = renderHook(() => useFlashcards())
    await act(async () => {
      await result.current.generate({ content: '   ', file: null, mode: 'auto' })
    })
    expect(result.current.status).toBe('error')
    expect(result.current.errorMessage).toMatch(/vazio/)
  })

  it('sets success with flashcard array on flashcards response', async () => {
    vi.mocked(service.generateFlashcards).mockResolvedValueOnce({
      artifact: [{ id: '1', question: 'Q?', answer: 'A' }],
      artifact_type: 'flashcards',
      mode: 'flashcards',
    } as any)

    const { result } = renderHook(() => useFlashcards())
    await act(async () => {
      await result.current.generate({ content: 'Test', file: null, mode: 'flashcards' })
    })
    expect(result.current.status).toBe('success')
    expect(result.current.artifact_type).toBe('flashcards')
    expect(Array.isArray(result.current.artifact)).toBe(true)
  })

  it('sets success with string artifact on summary response', async () => {
    vi.mocked(service.generateFlashcards).mockResolvedValueOnce({
      artifact: '# Resumo\nConteúdo.',
      artifact_type: 'summary',
      mode: 'summary',
    } as any)

    const { result } = renderHook(() => useFlashcards())
    await act(async () => {
      await result.current.generate({ content: 'Texto longo', file: null, mode: 'summary' })
    })
    expect(result.current.status).toBe('success')
    expect(result.current.artifact_type).toBe('summary')
    expect(typeof result.current.artifact).toBe('string')
  })

  it('sets error state on API error', async () => {
    const { ApiError } = await import('../services/flashcard.service')
    vi.mocked(service.generateFlashcards).mockRejectedValueOnce(
      new ApiError(500, 'Erro interno')
    )

    const { result } = renderHook(() => useFlashcards())
    await act(async () => {
      await result.current.generate({ content: 'Test', file: null, mode: 'auto' })
    })
    expect(result.current.status).toBe('error')
    expect(result.current.errorMessage).toBe('Erro interno')
  })

  it('reset clears all state', async () => {
    vi.mocked(service.generateFlashcards).mockResolvedValueOnce({
      artifact: [],
      artifact_type: 'flashcards',
      mode: 'auto',
    } as any)

    const { result } = renderHook(() => useFlashcards())
    await act(async () => {
      await result.current.generate({ content: 'Test', file: null, mode: 'auto' })
    })
    expect(result.current.status).toBe('success')

    act(() => { result.current.reset() })
    expect(result.current.status).toBe('idle')
    expect(result.current.artifact).toBeNull()
  })
})
