import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import MeusDicionarios from '../pages/MeusDicionarios'

const mockUpdateDicionario = vi.fn().mockResolvedValue(undefined)
const mockRemoveDicionario = vi.fn().mockResolvedValue(undefined)

const defaultDicionarios = [
  { id: 'd-1', topic: 'Biologia Celular', html: '<table><tr><th>Termo</th><th>Definição</th></tr><tr><td>Mitocôndria</td><td>Organela</td></tr></table>', termsCount: 1, date: '01/01/2024' },
  { id: 'd-2', topic: 'Química', html: '<table><tr></tr></table>', termsCount: 0, date: '02/01/2024' },
]

// vi.hoisted ensures this is available when vi.mock factory runs (hoisted above const declarations)
const mockUseFlashcards = vi.hoisted(() => vi.fn())

vi.mock('../contexts/FlashcardContext', () => ({
  useFlashcards: mockUseFlashcards,
}))

beforeEach(() => {
  vi.clearAllMocks()
  mockUseFlashcards.mockReturnValue({
    themes: [],
    resumos: [],
    dicionarios: defaultDicionarios,
    updateDicionario: mockUpdateDicionario,
    removeDicionario: mockRemoveDicionario,
  })
  mockUpdateDicionario.mockResolvedValue(undefined)
  mockRemoveDicionario.mockResolvedValue(undefined)
})

function renderMeusDicionarios() {
  return render(<MemoryRouter><MeusDicionarios /></MemoryRouter>)
}

describe('MeusDicionarios', () => {
  it('renders dicionario cards', () => {
    renderMeusDicionarios()
    expect(screen.getByText('Biologia Celular')).toBeInTheDocument()
    expect(screen.getByText('Química')).toBeInTheDocument()
  })

  it('renders empty state when no dicionarios', () => {
    mockUseFlashcards.mockReturnValueOnce({ themes: [], resumos: [], dicionarios: [], updateDicionario: mockUpdateDicionario, removeDicionario: mockRemoveDicionario })
    renderMeusDicionarios()
    expect(screen.getByText('Nenhum dicionário salvo ainda.')).toBeInTheDocument()
  })

  it('"Ver dicionário" opens view modal', async () => {
    renderMeusDicionarios()
    fireEvent.click(screen.getAllByText('Ver dicionário')[0])
    await waitFor(() => {
      expect(screen.getAllByText('Biologia Celular').length).toBeGreaterThanOrEqual(2)
    })
  })

  it('X button closes view modal', async () => {
    renderMeusDicionarios()
    fireEvent.click(screen.getAllByText('Ver dicionário')[0])
    await waitFor(() => expect(screen.getAllByText('Biologia Celular').length).toBeGreaterThanOrEqual(2))
    fireEvent.click(screen.getByRole('button', { name: /fechar/i }))
    await waitFor(() => expect(screen.getAllByText('Biologia Celular')).toHaveLength(1))
  })

  it('delete button opens confirmation modal', async () => {
    renderMeusDicionarios()
    fireEvent.click(screen.getAllByTitle('Excluir')[0])
    expect(await screen.findByText('Excluir dicionário?')).toBeInTheDocument()
  })

  it('confirm delete calls removeDicionario', async () => {
    renderMeusDicionarios()
    fireEvent.click(screen.getAllByTitle('Excluir')[0])
    await screen.findByText('Excluir dicionário?')
    fireEvent.click(screen.getByText('Excluir'))
    await waitFor(() => expect(mockRemoveDicionario).toHaveBeenCalledWith('d-1'))
  })
})
