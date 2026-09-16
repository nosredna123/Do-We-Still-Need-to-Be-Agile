import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import DeckDetail from '../pages/DeckDetail'

const mockNavigate = vi.fn()
const mockUpdateCard = vi.fn().mockResolvedValue(undefined)
const mockRemoveCard = vi.fn().mockResolvedValue(undefined)

const defaultCtx = {
  themes: [
    {
      id: 'deck-1',
      name: 'Guerra Fria',
      cards: [
        { id: 'c-1', question: 'Quando começou?', answer: '1947' },
        { id: 'c-2', question: 'Quando terminou?', answer: '1991' },
      ],
    },
  ],
  resumos: [],
  dicionarios: [],
  updateCard: mockUpdateCard,
  removeCard: mockRemoveCard,
}

const mockUseFlashcards = vi.hoisted(() => vi.fn())

vi.mock('../contexts/FlashcardContext', () => ({
  useFlashcards: mockUseFlashcards,
}))

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: () => mockNavigate }
})

vi.mock('gsap', () => ({
  gsap: { to: vi.fn() },
}))

beforeEach(() => {
  vi.clearAllMocks()
  mockUseFlashcards.mockReturnValue(defaultCtx)
  mockUpdateCard.mockResolvedValue(undefined)
  mockRemoveCard.mockResolvedValue(undefined)
})

function renderDeck(deckId = 'deck-1') {
  return render(
    <MemoryRouter initialEntries={[`/meus-cards/${deckId}`]}>
      <Routes>
        <Route path="/meus-cards/:deckId" element={<DeckDetail />} />
      </Routes>
    </MemoryRouter>
  )
}

describe('DeckDetail', () => {
  it('renders deck name and cards', () => {
    renderDeck()
    expect(screen.getByText('Guerra Fria')).toBeInTheDocument()
    expect(screen.getByText('Quando começou?')).toBeInTheDocument()
    expect(screen.getByText('Quando terminou?')).toBeInTheDocument()
  })

  it('back button navigates to /meus-cards', () => {
    renderDeck()
    fireEvent.click(screen.getByText('Voltar'))
    expect(mockNavigate).toHaveBeenCalledWith('/meus-cards')
  })

  it('renders "not found" for unknown deckId', () => {
    renderDeck('unknown-id')
    expect(screen.getByText('Deck não encontrado')).toBeInTheDocument()
  })

  it('edit card opens modal with question and answer', async () => {
    renderDeck()
    const editButtons = screen.getAllByTitle('Editar card')
    fireEvent.click(editButtons[0])
    expect(await screen.findByText('Editar Card')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Quando começou?')).toBeInTheDocument()
    expect(screen.getByDisplayValue('1947')).toBeInTheDocument()
  })

  it('delete card opens confirmation modal', async () => {
    renderDeck()
    const deleteButtons = screen.getAllByTitle('Excluir card')
    fireEvent.click(deleteButtons[0])
    expect(await screen.findByText('Excluir Card?')).toBeInTheDocument()
  })

  it('confirm delete calls removeCard', async () => {
    renderDeck()
    const deleteButtons = screen.getAllByTitle('Excluir card')
    fireEvent.click(deleteButtons[0])
    await screen.findByText('Excluir Card?')
    fireEvent.click(screen.getByText('Sim, excluir'))
    await waitFor(() => expect(mockRemoveCard).toHaveBeenCalledWith('c-1'))
  })
})
