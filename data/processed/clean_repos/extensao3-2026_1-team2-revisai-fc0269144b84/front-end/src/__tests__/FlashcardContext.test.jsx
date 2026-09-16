import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, act, waitFor } from '@testing-library/react'
import { FlashcardProvider, useFlashcards } from '../contexts/FlashcardContext'

// ── Mock all service functions ──────────────────────────────────────────────
vi.mock('../services/flashcard.service', () => ({
  fetchFlashcards: vi.fn().mockResolvedValue([]),
  saveFlashcard: vi.fn().mockResolvedValue({ id: 'saved-1', question: 'Q?', answer: 'A', themeName: 'T', createdAt: '' }),
  updateFlashcard: vi.fn().mockResolvedValue(undefined),
  deleteFlashcard: vi.fn().mockResolvedValue(undefined),
  fetchResumos: vi.fn().mockResolvedValue([]),
  saveResumo: vi.fn().mockResolvedValue({ id: 'r-1', topic: 'T', html: '<p>x</p>', createdAt: '' }),
  updateResumo: vi.fn().mockResolvedValue(undefined),
  deleteResumo: vi.fn().mockResolvedValue(undefined),
  fetchDicionarios: vi.fn().mockResolvedValue([]),
  saveDicionario: vi.fn().mockResolvedValue({ id: 'd-1', topic: 'D', html: '<p>d</p>', termsCount: 2, createdAt: '' }),
  updateDicionario: vi.fn().mockResolvedValue(undefined),
  deleteDicionario: vi.fn().mockResolvedValue(undefined),
}))

import * as svc from '../services/flashcard.service'

beforeEach(() => { vi.clearAllMocks() })

// ── Test helper ─────────────────────────────────────────────────────────────
function renderCtx() {
  let ctx
  function Consumer() {
    ctx = useFlashcards()
    return null
  }
  render(<FlashcardProvider><Consumer /></FlashcardProvider>)
  return () => ctx
}

// ── Tests ────────────────────────────────────────────────────────────────────

describe('FlashcardContext — flashcard operations', () => {
  it('addGeneratedCards calls saveFlashcard for each card and updates themes', async () => {
    const getCtx = renderCtx()
    await act(async () => {
      await getCtx().addGeneratedCards('History', [
        { id: 'tmp-1', question: 'Q1?', answer: 'A1' },
        { id: 'tmp-2', question: 'Q2?', answer: 'A2' },
      ])
    })
    expect(svc.saveFlashcard).toHaveBeenCalledTimes(2)
    expect(svc.saveFlashcard).toHaveBeenCalledWith({ question: 'Q1?', answer: 'A1', themeName: 'History' })
    await waitFor(() => {
      expect(getCtx().themes).toHaveLength(1)
      expect(getCtx().themes[0].name).toBe('History')
    })
  })

  it('renameTheme calls updateFlashcard with new themeName for all cards', async () => {
    vi.mocked(svc.fetchFlashcards).mockResolvedValue([
      { id: 'c1', question: 'Q?', answer: 'A', themeName: 'Old', createdAt: '' },
      { id: 'c2', question: 'Q2?', answer: 'A2', themeName: 'Old', createdAt: '' },
    ])
    const getCtx = renderCtx()
    await waitFor(() => expect(getCtx().themes).toHaveLength(1))

    await act(async () => {
      await getCtx().renameTheme('Old', 'New')
    })
    expect(svc.updateFlashcard).toHaveBeenCalledTimes(2)
    expect(svc.updateFlashcard).toHaveBeenCalledWith('c1', { themeName: 'New' })
    expect(svc.updateFlashcard).toHaveBeenCalledWith('c2', { themeName: 'New' })
    expect(getCtx().themes[0].name).toBe('New')
  })

  it('deleteTheme calls deleteFlashcard for all cards and removes theme', async () => {
    vi.mocked(svc.fetchFlashcards).mockResolvedValue([
      { id: 'c1', question: 'Q?', answer: 'A', themeName: 'Science', createdAt: '' },
    ])
    const getCtx = renderCtx()
    await waitFor(() => expect(getCtx().themes).toHaveLength(1))

    await act(async () => {
      await getCtx().deleteTheme('Science')
    })
    expect(svc.deleteFlashcard).toHaveBeenCalledWith('c1')
    expect(getCtx().themes).toHaveLength(0)
  })

  it('removeCard calls deleteFlashcard and removes from state', async () => {
    vi.mocked(svc.fetchFlashcards).mockResolvedValue([
      { id: 'c1', question: 'Q?', answer: 'A', themeName: 'T', createdAt: '' },
    ])
    const getCtx = renderCtx()
    await waitFor(() => expect(getCtx().themes[0].cards).toHaveLength(1))

    await act(async () => { await getCtx().removeCard('c1') })
    expect(svc.deleteFlashcard).toHaveBeenCalledWith('c1')
    expect(getCtx().themes).toHaveLength(0) // theme removed when empty
  })
})

describe('FlashcardContext — resumo operations', () => {
  it('addResumo calls saveResumo and updates resumos list', async () => {
    const getCtx = renderCtx()
    await act(async () => {
      await getCtx().addResumo('Topic A', '<p>html</p>')
    })
    expect(svc.saveResumo).toHaveBeenCalledWith({ topic: 'Topic A', html: '<p>html</p>' })
    await waitFor(() => expect(getCtx().resumos).toHaveLength(1))
  })

  it('updateResumo calls API and updates local topic', async () => {
    vi.mocked(svc.fetchResumos).mockResolvedValue([
      { id: 'r-1', topic: 'Old', html: '<p>x</p>', createdAt: '2024-01-01T00:00:00Z' },
    ])
    const getCtx = renderCtx()
    await waitFor(() => expect(getCtx().resumos).toHaveLength(1))

    await act(async () => { await getCtx().updateResumo('r-1', 'New Topic') })
    expect(svc.updateResumo).toHaveBeenCalledWith('r-1', { topic: 'New Topic' })
    expect(getCtx().resumos[0].topic).toBe('New Topic')
  })

  it('removeResumo calls deleteResumo and removes from list', async () => {
    vi.mocked(svc.fetchResumos).mockResolvedValue([
      { id: 'r-1', topic: 'T', html: '<p>x</p>', createdAt: '2024-01-01T00:00:00Z' },
    ])
    const getCtx = renderCtx()
    await waitFor(() => expect(getCtx().resumos).toHaveLength(1))

    await act(async () => { await getCtx().removeResumo('r-1') })
    expect(svc.deleteResumo).toHaveBeenCalledWith('r-1')
    expect(getCtx().resumos).toHaveLength(0)
  })
})

describe('FlashcardContext — dicionario operations', () => {
  it('addDicionario calls saveDicionario and updates list', async () => {
    const getCtx = renderCtx()
    await act(async () => {
      await getCtx().addDicionario('Dict A', '<table/>', 5)
    })
    expect(svc.saveDicionario).toHaveBeenCalledWith({ topic: 'Dict A', html: '<table/>', termsCount: 5 })
    await waitFor(() => expect(getCtx().dicionarios).toHaveLength(1))
  })

  it('updateDicionario calls API and updates local topic', async () => {
    vi.mocked(svc.fetchDicionarios).mockResolvedValue([
      { id: 'd-1', topic: 'Old Dict', html: '<table/>', termsCount: 2, createdAt: '2024-01-01T00:00:00Z' },
    ])
    const getCtx = renderCtx()
    await waitFor(() => expect(getCtx().dicionarios).toHaveLength(1))

    await act(async () => { await getCtx().updateDicionario('d-1', 'New Dict') })
    expect(svc.updateDicionario).toHaveBeenCalledWith('d-1', { topic: 'New Dict' })
    expect(getCtx().dicionarios[0].topic).toBe('New Dict')
  })

  it('removeDicionario calls deleteDicionario and removes from list', async () => {
    vi.mocked(svc.fetchDicionarios).mockResolvedValue([
      { id: 'd-1', topic: 'D', html: '<table/>', termsCount: 1, createdAt: '2024-01-01T00:00:00Z' },
    ])
    const getCtx = renderCtx()
    await waitFor(() => expect(getCtx().dicionarios).toHaveLength(1))

    await act(async () => { await getCtx().removeDicionario('d-1') })
    expect(svc.deleteDicionario).toHaveBeenCalledWith('d-1')
    expect(getCtx().dicionarios).toHaveLength(0)
  })
})
