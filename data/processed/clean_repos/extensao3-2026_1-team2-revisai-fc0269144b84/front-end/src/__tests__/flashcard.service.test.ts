import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  generateFlashcards,
  fetchFlashcards,
  saveFlashcard,
  updateFlashcard,
  deleteFlashcard,
  fetchResumos,
  saveResumo,
  updateResumo,
  deleteResumo,
  saveDicionario,
  deleteDicionario,
  ApiError,
  NetworkError,
} from '../services/flashcard.service'

const BASE = 'http://localhost:5000'

function mockFetch(status: number, body: unknown) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    json: () => Promise.resolve(body),
  } as Response)
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('generateFlashcards', () => {
  it('returns response on success', async () => {
    const payload = { artifact: [], artifact_type: 'flashcards', mode: 'auto' }
    globalThis.fetch = mockFetch(200, payload)
    const result = await generateFlashcards({ content: 'Test content' })
    expect(result).toEqual(payload)
  })

  it('throws ApiError on HTTP error', async () => {
    globalThis.fetch = mockFetch(422, { message: 'Validation error' })
    const err = await generateFlashcards({ content: 'x' }).catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect((err as ApiError).statusCode).toBe(422)
  })

  it('throws NetworkError on network failure', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))
    await expect(generateFlashcards({ content: 'x' })).rejects.toBeInstanceOf(NetworkError)
  })
})

describe('fetchFlashcards', () => {
  it('returns array on success', async () => {
    const cards = [{ id: '1', question: 'Q?', answer: 'A', themeName: 'T', createdAt: '' }]
    globalThis.fetch = mockFetch(200, cards)
    const result = await fetchFlashcards()
    expect(result).toEqual(cards)
  })
})

describe('saveFlashcard', () => {
  it('returns saved card on success', async () => {
    const card = { question: 'Q?', answer: 'A', themeName: 'T', createdAt: '' }
    globalThis.fetch = mockFetch(201, { id: 'new-id', flashcard: card })
    const result = await saveFlashcard({ question: 'Q?', answer: 'A', themeName: 'T' })
    expect(result.id).toBe('new-id')
    expect(result.question).toBe('Q?')
  })
})

describe('updateFlashcard', () => {
  it('calls PUT and succeeds', async () => {
    globalThis.fetch = mockFetch(200, { message: 'ok' })
    await expect(updateFlashcard('id-1', { question: 'New Q' })).resolves.toBeUndefined()
    expect((globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0]).toBe(`${BASE}/api/flashcards/id-1`)
  })
})

describe('deleteFlashcard', () => {
  it('calls DELETE and succeeds', async () => {
    globalThis.fetch = mockFetch(200, { message: 'ok' })
    await expect(deleteFlashcard('id-1')).resolves.toBeUndefined()
    expect((globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0][1]?.method).toBe('DELETE')
  })
})

describe('fetchResumos', () => {
  it('returns array on success', async () => {
    const resumos = [{ id: '1', topic: 'T', html: '<p>x</p>', createdAt: '' }]
    globalThis.fetch = mockFetch(200, resumos)
    const result = await fetchResumos()
    expect(result).toEqual(resumos)
  })
})

describe('saveResumo', () => {
  it('returns saved resumo', async () => {
    const resumo = { topic: 'T', html: '<p>x</p>', createdAt: '' }
    globalThis.fetch = mockFetch(201, { id: 'r-1', resumo })
    const result = await saveResumo({ topic: 'T', html: '<p>x</p>' })
    expect(result.id).toBe('r-1')
    expect(result.topic).toBe('T')
  })
})

describe('updateResumo', () => {
  it('calls PUT on resumo', async () => {
    globalThis.fetch = mockFetch(200, { message: 'ok' })
    await expect(updateResumo('r-1', { topic: 'New' })).resolves.toBeUndefined()
    expect((globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0]).toBe(`${BASE}/api/resumos/r-1`)
  })
})

describe('deleteResumo', () => {
  it('calls DELETE on resumo', async () => {
    globalThis.fetch = mockFetch(200, { message: 'ok' })
    await expect(deleteResumo('r-1')).resolves.toBeUndefined()
  })
})

describe('saveDicionario', () => {
  it('returns saved dicionario', async () => {
    const dic = { topic: 'D', html: '<table/>', termsCount: 3, createdAt: '' }
    globalThis.fetch = mockFetch(201, { id: 'd-1', dicionario: dic })
    const result = await saveDicionario({ topic: 'D', html: '<table/>', termsCount: 3 })
    expect(result.id).toBe('d-1')
  })
})

describe('deleteDicionario', () => {
  it('calls DELETE on dicionario', async () => {
    globalThis.fetch = mockFetch(200, { message: 'ok' })
    await expect(deleteDicionario('d-1')).resolves.toBeUndefined()
  })
})
