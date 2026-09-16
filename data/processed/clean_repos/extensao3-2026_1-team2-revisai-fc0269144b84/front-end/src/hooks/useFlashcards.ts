import { useState, useCallback } from "react";
import { generateFlashcards, ApiError, NetworkError } from "../services/flashcard.service";
import type { Flashcard, RequestStatus, ChatMessage } from "../types/flashcard.types";


interface UseFlashcardsReturn {
  artifact: Flashcard[] | string | null;
  artifact_type: string | null;
  tema: string | null;
  router_decision: string | null;
  status: RequestStatus;
  errorMessage: string | null;
  generate: (params: { content: string; file?: File | null; mode: string; history?: ChatMessage[] }) => Promise<void>;
  reset: () => void;
}

const fileToBase64 = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve((reader.result as string).split(',')[1]);
    reader.onerror = error => reject(error);
  });

function parseFlashcards(markdown: string | null | undefined): Flashcard[] {
  if (!markdown) return [];

  const blocks = markdown.split("---").filter(b => b.trim());

  const cards = blocks
    .filter(b => b.includes("Flashcard"))
    .map((block, i) => {
      const pergunta = block.match(/\*\*Pergunta:\*\*\s*([\s\S]+?)\n\n\*\*Resposta:/)?.[1]?.trim() ?? "";
      const resposta = block.match(/\*\*Resposta:\*\*\s*([\s\S]+?)(?:\n\n|$)/)?.[1]?.trim() ?? "";
      return {
        id: `card-${Date.now()}-${i}`,
        question: pergunta,
        answer: resposta,
      };
    })
    .filter(card => card.question && card.answer);

  return cards;
}

export function useFlashcards(): UseFlashcardsReturn {
  const [artifact, setArtifact] = useState<Flashcard[] | string | null>(null);
  const [artifact_type, setArtifactType] = useState<string | null>(null);
  const [tema, setTema] = useState<string | null>(null);
  const [router_decision, setRouterDecision] = useState<string | null>(null);
  const [status, setStatus] = useState<RequestStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const generate = useCallback(async ({ content, file, mode, history }: { content: string; file?: File | null; mode: string; history?: ChatMessage[] }) => {
    if (!content.trim() && !file) {
      setErrorMessage("O conteúdo não pode estar vazio.");
      setStatus("error");
      return;
    }

    setStatus("loading");
    setErrorMessage(null);
    setArtifact(null);
    setArtifactType(null);
    setTema(null);
    setRouterDecision(null);

    try {
      const payload: any = {
        content: content.trim(),
        mode,
      };

      if (history && history.length > 0) {
        payload.history = history;
      }

      if (file) {
        const ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'webp'];
        const ext = file.name.split('.').pop()?.toLowerCase();
        if (!ext || !ALLOWED_EXTENSIONS.includes(ext)) {
          setErrorMessage(`Tipo de arquivo não suportado: .${ext || '?'}. Use PDF, PNG, JPG ou WebP.`);
          setStatus("error");
          return;
        }
        payload.file_base64 = await fileToBase64(file);
        payload.file_name = file.name;
        payload.file_type = ext;
      }

      const data = await generateFlashcards(payload);

      if (data.artifact_type === "flashcards") {
        setArtifact(Array.isArray(data.artifact) ? data.artifact : parseFlashcards(data.artifact as string));
      } else {
        setArtifact(data.artifact as string);
      }

      setArtifactType(data.artifact_type);
      setTema(data.tema || null);
      setRouterDecision(data.router_decision || null);
      setStatus("success");

    } catch (err) {
      const message =
        err instanceof ApiError || err instanceof NetworkError
          ? err.message
          : "Ocorreu um erro inesperado. Tente novamente.";

      setErrorMessage(message);
      setStatus("error");
    }
  }, []);

  const reset = useCallback(() => {
    setArtifact(null);
    setArtifactType(null);
    setTema(null);
    setRouterDecision(null);
    setStatus("idle");
    setErrorMessage(null);
  }, []);

  return { artifact, artifact_type, tema, router_decision, status, errorMessage, generate, reset };
}
