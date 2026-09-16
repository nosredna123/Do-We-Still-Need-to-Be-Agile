import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import GerarFlashcards from '../pages/GerarFlashcards'

// ── Stored mock references (vi.hoisted so they survive vi.mock factory hoisting) ─

const mockGenerate = vi.fn().mockResolvedValue(undefined)
const mockAddGeneratedCards = vi.fn().mockResolvedValue(undefined)
const mockAddResumo = vi.fn().mockResolvedValue(undefined)
const mockAddDicionario = vi.fn().mockResolvedValue(undefined)

const mockUseFlashcardsCtx = vi.hoisted(() => vi.fn())
const mockUseFlashcardsApi = vi.hoisted(() => vi.fn())

vi.mock('../contexts/FlashcardContext', () => ({
  useFlashcards: mockUseFlashcardsCtx,
}))

vi.mock('../hooks/useFlashcards', () => ({
  useFlashcards: mockUseFlashcardsApi,
}))

vi.mock('../services/session.service', () => ({
  saveSession: vi.fn().mockResolvedValue(undefined),
  loadLastSession: vi.fn().mockResolvedValue(null),
  startNewSession: vi.fn(),
}))

vi.mock('marked', () => ({
  marked: { parse: vi.fn((s) => `<p>${s}</p>`) },
}))

const defaultCtxState = {
  themes: [],
  resumos: [],
  dicionarios: [],
  addGeneratedCards: mockAddGeneratedCards,
  removeCard: vi.fn(),
  addResumo: mockAddResumo,
  addDicionario: mockAddDicionario,
}

const idleApiState = {
  generate: mockGenerate,
  artifact: null,
  artifact_type: null,
  router_decision: null,
  status: 'idle',
  errorMessage: null,
}

beforeEach(() => {
  vi.clearAllMocks()
  mockUseFlashcardsCtx.mockReturnValue(defaultCtxState)
  mockUseFlashcardsApi.mockReturnValue(idleApiState)
  mockGenerate.mockResolvedValue(undefined)
})

function renderGerar() {
  return render(<MemoryRouter><GerarFlashcards /></MemoryRouter>)
}

describe('GerarFlashcards — chat interface', () => {
  it('renders welcome message for auto mode', () => {
    renderGerar()
    expect(screen.getByText(/Sou o RevisAI/)).toBeInTheDocument()
  })

  it('input starts empty', () => {
    renderGerar()
    const input = screen.getByPlaceholderText(/Informe o tema/)
    expect(input).toHaveValue('')
  })

  it('typing into input changes value', async () => {
    renderGerar()
    const input = screen.getByPlaceholderText(/Informe o tema/)
    await userEvent.type(input, 'Guerra Fria')
    expect(input).toHaveValue('Guerra Fria')
  })

  it('sending message shows user bubble', async () => {
    renderGerar()
    const input = screen.getByPlaceholderText(/Informe o tema/)
    await userEvent.type(input, 'Fotossíntese')
    fireEvent.keyDown(input, { key: 'Enter' })
    await waitFor(() => {
      expect(screen.getByText('Fotossíntese')).toBeInTheDocument()
    })
    expect(mockGenerate).toHaveBeenCalledWith(
      expect.objectContaining({ content: 'Fotossíntese', mode: 'auto' })
    )
  })

  it('mode button shows label when non-auto mode selected', async () => {
    renderGerar()
    const modeBtn = screen.getByTitle('Trocar modo')
    fireEvent.click(modeBtn)
    fireEvent.click(screen.getByText('Flashcards'))
    await waitFor(() => {
      expect(screen.getByText('Flashcards')).toBeInTheDocument()
    })
  })

  it('mode change updates welcome message', async () => {
    renderGerar()
    const modeBtn = screen.getByTitle('Trocar modo')
    fireEvent.click(modeBtn)
    fireEvent.click(screen.getByText('Resumo'))
    await waitFor(() => {
      expect(screen.getByText(/Modo Resumo ativado/)).toBeInTheDocument()
    })
  })

  it('shows error message when API returns error status', async () => {
    mockUseFlashcardsApi.mockReturnValue({
      generate: mockGenerate,
      artifact: null,
      artifact_type: null,
      router_decision: null,
      status: 'error',
      errorMessage: 'Falha na geração',
    })
    renderGerar()
    const input = screen.getByPlaceholderText(/Informe o tema/)
    await userEvent.type(input, 'test')
    fireEvent.keyDown(input, { key: 'Enter' })
    await waitFor(() => {
      expect(screen.getByText('Falha na geração')).toBeInTheDocument()
    })
  })
})
