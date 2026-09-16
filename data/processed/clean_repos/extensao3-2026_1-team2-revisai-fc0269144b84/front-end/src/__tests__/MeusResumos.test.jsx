import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import MeusResumos from '../pages/MeusResumos'

const mockUpdateResumo = vi.fn().mockResolvedValue(undefined)
const mockRemoveResumo = vi.fn().mockResolvedValue(undefined)

const defaultResumos = [
  { id: 'r-1', topic: 'Fotossíntese', html: '<p>Processo de conversão de luz em energia.</p>', date: '01/01/2024' },
  { id: 'r-2', topic: 'Mitose', html: '<p>Divisão celular.</p>', date: '02/01/2024' },
]

const mockUseFlashcards = vi.hoisted(() => vi.fn())

vi.mock('../contexts/FlashcardContext', () => ({
  useFlashcards: mockUseFlashcards,
}))

beforeEach(() => {
  vi.clearAllMocks()
  mockUseFlashcards.mockReturnValue({
    themes: [],
    resumos: defaultResumos,
    dicionarios: [],
    updateResumo: mockUpdateResumo,
    removeResumo: mockRemoveResumo,
  })
  mockUpdateResumo.mockResolvedValue(undefined)
  mockRemoveResumo.mockResolvedValue(undefined)
})

function renderMeusResumos() {
  return render(<MemoryRouter><MeusResumos /></MemoryRouter>)
}

describe('MeusResumos', () => {
  it('renders resumo cards', () => {
    renderMeusResumos()
    expect(screen.getByText('Fotossíntese')).toBeInTheDocument()
    expect(screen.getByText('Mitose')).toBeInTheDocument()
  })

  it('renders empty state when no resumos', () => {
    mockUseFlashcards.mockReturnValueOnce({ themes: [], resumos: [], dicionarios: [], updateResumo: mockUpdateResumo, removeResumo: mockRemoveResumo })
    renderMeusResumos()
    expect(screen.getByText('Nenhum resumo salvo ainda.')).toBeInTheDocument()
  })

  it('"Ver resumo" opens view modal', async () => {
    renderMeusResumos()
    fireEvent.click(screen.getAllByText('Ver resumo')[0])
    await waitFor(() => {
      expect(screen.getAllByText('Fotossíntese').length).toBeGreaterThanOrEqual(2)
    })
  })

  it('X button closes view modal', async () => {
    renderMeusResumos()
    fireEvent.click(screen.getAllByText('Ver resumo')[0])
    await waitFor(() => expect(screen.getAllByText('Fotossíntese').length).toBeGreaterThanOrEqual(2))
    fireEvent.click(screen.getByRole('button', { name: /fechar/i }))
    await waitFor(() => {
      expect(screen.getAllByText('Fotossíntese')).toHaveLength(1)
    })
  })

  it('delete button opens confirmation modal', async () => {
    renderMeusResumos()
    fireEvent.click(screen.getAllByTitle('Excluir')[0])
    expect(await screen.findByText('Excluir resumo?')).toBeInTheDocument()
  })

  it('confirm delete calls removeResumo', async () => {
    renderMeusResumos()
    fireEvent.click(screen.getAllByTitle('Excluir')[0])
    await screen.findByText('Excluir resumo?')
    fireEvent.click(screen.getByText('Excluir'))
    await waitFor(() => expect(mockRemoveResumo).toHaveBeenCalledWith('r-1'))
  })

  it('edit pencil shows inline input with current topic', async () => {
    renderMeusResumos()
    fireEvent.click(screen.getAllByTitle('Editar nome')[0])
    expect(screen.getByDisplayValue('Fotossíntese')).toBeInTheDocument()
  })
})
