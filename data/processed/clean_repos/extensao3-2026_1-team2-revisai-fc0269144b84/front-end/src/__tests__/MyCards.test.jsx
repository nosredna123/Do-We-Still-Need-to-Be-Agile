import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import MyCards from '../pages/MyCards'

const mockDeleteTheme = vi.fn().mockResolvedValue(undefined)
const mockRenameTheme = vi.fn().mockResolvedValue(undefined)
const mockNavigate = vi.fn()

// Full context shape — Sidebar also reads themes/resumos/dicionarios
const defaultCtx = {
  themes: [
    { id: 'theme-1', name: 'Guerra Fria', description: 'Cards sobre Guerra Fria', progress: 0, cards: [{ id: 'c1', question: 'Q?', answer: 'A' }] },
    { id: 'theme-2', name: 'Física', description: 'Cards sobre Física', progress: 50, cards: [] },
  ],
  resumos: [],
  dicionarios: [],
  renameTheme: mockRenameTheme,
  deleteTheme: mockDeleteTheme,
}

const mockUseFlashcards = vi.hoisted(() => vi.fn())

vi.mock('../contexts/FlashcardContext', () => ({
  useFlashcards: mockUseFlashcards,
}))

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: () => mockNavigate }
})

beforeEach(() => {
  vi.clearAllMocks()
  mockUseFlashcards.mockReturnValue(defaultCtx)
  mockDeleteTheme.mockResolvedValue(undefined)
  mockRenameTheme.mockResolvedValue(undefined)
})

function renderMyCards() {
  return render(<MemoryRouter><MyCards /></MemoryRouter>)
}

describe('MyCards', () => {
  it('renders all theme cards', () => {
    renderMyCards()
    expect(screen.getByText('Guerra Fria')).toBeInTheDocument()
    expect(screen.getByText('Física')).toBeInTheDocument()
    expect(screen.getByText('2 temas disponíveis')).toBeInTheDocument()
  })

  it('clicking card navigates to deck detail', async () => {
    renderMyCards()
    await userEvent.click(screen.getByText('Guerra Fria'))
    expect(mockNavigate).toHaveBeenCalledWith('/meus-cards/theme-1')
  })

  it('delete button opens confirmation modal', async () => {
    renderMyCards()
    const deleteButtons = screen.getAllByTitle('Excluir tema')
    fireEvent.click(deleteButtons[0])
    expect(await screen.findByText('Excluir tema?')).toBeInTheDocument()
    expect(screen.getByText(/Todos os cards deste tema serão excluídos/)).toBeInTheDocument()
  })

  it('cancel button closes delete modal', async () => {
    renderMyCards()
    fireEvent.click(screen.getAllByTitle('Excluir tema')[0])
    await screen.findByText('Excluir tema?')
    fireEvent.click(screen.getByText('Cancelar'))
    await waitFor(() => expect(screen.queryByText('Excluir tema?')).not.toBeInTheDocument())
  })

  it('confirm delete calls deleteTheme', async () => {
    renderMyCards()
    fireEvent.click(screen.getAllByTitle('Excluir tema')[0])
    await screen.findByText('Excluir tema?')
    fireEvent.click(screen.getByText('Excluir'))
    await waitFor(() => expect(mockDeleteTheme).toHaveBeenCalledWith('theme-1'))
  })

  it('edit button shows inline input', async () => {
    renderMyCards()
    fireEvent.click(screen.getAllByTitle('Renomear tema')[0])
    expect(screen.getByDisplayValue('Guerra Fria')).toBeInTheDocument()
  })

  it('escape key cancels edit without saving', async () => {
    renderMyCards()
    fireEvent.click(screen.getAllByTitle('Renomear tema')[0])
    const input = screen.getByDisplayValue('Guerra Fria')
    fireEvent.keyDown(input, { key: 'Escape' })
    await waitFor(() => expect(screen.queryByDisplayValue('Guerra Fria')).not.toBeInTheDocument())
    expect(mockRenameTheme).not.toHaveBeenCalled()
  })
})
