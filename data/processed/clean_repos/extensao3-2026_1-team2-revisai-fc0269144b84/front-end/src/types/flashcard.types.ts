export interface Flashcard {
  id: string;
  question: string;
  answer: string;
}

export interface SavedFlashcard {
  id: string;
  question: string;
  answer: string;
  themeName: string;
  createdAt: string;
  updatedAt?: string;
}

// Mensagem do histórico de conversa enviada à Lambda
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface GenerateFlashcardsPayload {
  content: string;
  file_base64?: string;
  file_type?: string;
  file_name?: string;
  mode?: string;
  history?: ChatMessage[];
}

// Para flashcards: server.js já parseia o Markdown e envia Flashcard[]
// Para summary/glossary: artifact chega como string Markdown
export interface GenerateFlashcardsResponse {
  artifact: Flashcard[] | string;
  artifact_type: string;
  tema?: string;
  mode: string;
  model?: string;
  router_decision?: string;
}

export interface SavedResumo {
  id: string;
  topic: string;
  html: string;
  createdAt: string;
}

export interface SavedDicionario {
  id: string;
  topic: string;
  html: string;
  termsCount: number;
  createdAt: string;
}

export type RequestStatus = "idle" | "loading" | "success" | "error";
