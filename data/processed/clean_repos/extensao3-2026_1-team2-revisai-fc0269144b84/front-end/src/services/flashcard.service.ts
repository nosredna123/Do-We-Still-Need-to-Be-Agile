
import { auth } from "../../firebase";
import type {
  GenerateFlashcardsPayload,
  GenerateFlashcardsResponse,
  SavedFlashcard,
  SavedResumo,
  SavedDicionario,
} from "../types/flashcard.types";

const API_BASE_URL = "http://localhost:5000";

async function authHeaders(): Promise<Record<string, string>> {
  const user = auth.currentUser;
  const base: Record<string, string> = { "Content-Type": "application/json" };
  if (!user) return base;
  const token = await user.getIdToken();
  return { ...base, Authorization: `Bearer ${token}` };
}

// Erros customizados para facilitar o tratamento por camada
export class ApiError extends Error {
  constructor(
    public readonly statusCode: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class NetworkError extends Error {
  constructor() {
    super("Falha de conexão. Verifique sua internet e tente novamente.");
    this.name = "NetworkError";
  }
}

/**
 * Gera flashcards a partir de um conteúdo textual.
 * Lança ApiError para respostas HTTP com erro, ou NetworkError para falhas de rede.
 */
export async function generateFlashcards(
  payload: GenerateFlashcardsPayload
): Promise<GenerateFlashcardsResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/api/generate-flashcards`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new NetworkError();
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      errorBody?.message ?? `Erro ${response.status}: ${response.statusText}`
    );
  }

  return response.json() as Promise<GenerateFlashcardsResponse>;
}

export async function fetchFlashcards(): Promise<SavedFlashcard[]> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/flashcards`, {
      headers: await authHeaders(),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
  return response.json();
}

export async function saveFlashcard(
  card: { question: string; answer: string; themeName: string }
): Promise<SavedFlashcard> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/flashcards`, {
      method: "POST",
      headers: await authHeaders(),
      body: JSON.stringify(card),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
  const { id, flashcard } = await response.json();
  return { id, ...flashcard } as SavedFlashcard;
}

export async function updateFlashcard(
  id: string,
  data: { question?: string; answer?: string; themeName?: string }
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/flashcards/${id}`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify(data),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
}

export async function deleteFlashcard(id: string): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/flashcards/${id}`, {
      method: "DELETE",
      headers: await authHeaders(),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
}

// ── RESUMOS ────────────────────────────────────────────────────────────────

export async function fetchResumos(): Promise<SavedResumo[]> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/resumos`, {
      headers: await authHeaders(),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
  return response.json();
}

export async function saveResumo(
  resumo: { topic: string; html: string }
): Promise<SavedResumo> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/resumos`, {
      method: "POST",
      headers: await authHeaders(),
      body: JSON.stringify(resumo),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
  const { id, resumo: saved } = await response.json();
  return { id, ...saved } as SavedResumo;
}

export async function updateResumo(
  id: string,
  data: { topic: string }
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/resumos/${id}`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify(data),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
}

export async function deleteResumo(id: string): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/resumos/${id}`, {
      method: "DELETE",
      headers: await authHeaders(),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
}

// ── DICIONÁRIOS ─────────────────────────────────────────────────────────────

export async function fetchDicionarios(): Promise<SavedDicionario[]> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/dicionarios`, {
      headers: await authHeaders(),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
  return response.json();
}

export async function saveDicionario(
  dicionario: { topic: string; html: string; termsCount?: number }
): Promise<SavedDicionario> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/dicionarios`, {
      method: "POST",
      headers: await authHeaders(),
      body: JSON.stringify(dicionario),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
  const { id, dicionario: saved } = await response.json();
  return { id, ...saved } as SavedDicionario;
}

export async function updateDicionario(
  id: string,
  data: { topic: string }
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/dicionarios/${id}`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify(data),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
}

export async function deleteDicionario(id: string): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/dicionarios/${id}`, {
      method: "DELETE",
      headers: await authHeaders(),
    });
  } catch {
    throw new NetworkError();
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorBody?.error ?? `Erro ${response.status}`);
  }
}