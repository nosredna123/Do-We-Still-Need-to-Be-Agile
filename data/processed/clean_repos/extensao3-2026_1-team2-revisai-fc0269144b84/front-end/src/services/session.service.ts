import {
  collection,
  doc,
  setDoc,
  query,
  orderBy,
  limit,
  getDocs,
  serverTimestamp,
} from "firebase/firestore";
import { db } from "../lib/firebase";
import type { ChatMessage } from "../types/flashcard.types";

const ANONYMOUS_UID_KEY = "revisai_anonymous_uid";
const SESSION_ID_KEY = "revisai_session_id";

/** UUID persistente por navegador — identifica o "usuário" anônimo */
function getOrCreateAnonymousUid(): string {
  let uid = localStorage.getItem(ANONYMOUS_UID_KEY);
  if (!uid) {
    uid = crypto.randomUUID();
    localStorage.setItem(ANONYMOUS_UID_KEY, uid);
  }
  return uid;
}

/** UUID persistente por navegador — identifica a sessão de conversa */
function getOrCreateSessionId(): string {
  let sessionId = localStorage.getItem(SESSION_ID_KEY);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_ID_KEY, sessionId);
  }
  return sessionId;
}

/**
 * Persiste o histórico de conversa e as mensagens da UI no Firestore.
 * Usa merge para não sobrescrever o campo createdAt na primeira gravação.
 */
export async function saveSession(
  conversationHistory: ChatMessage[],
  messages: object[]
): Promise<void> {
  const uid = getOrCreateAnonymousUid();
  const sessionId = getOrCreateSessionId();
  const sessionRef = doc(collection(db, "users", uid, "sessions"), sessionId);

  await setDoc(
    sessionRef,
    {
      updatedAt: serverTimestamp(),
      createdAt: serverTimestamp(), // ignorado no merge se já existir
      history: conversationHistory,
      messages,
    },
    { merge: true }
  );
}

/**
 * Carrega a última sessão salva para este navegador.
 * Retorna null se não houver sessão ou ocorrer algum erro.
 */
export async function loadLastSession(): Promise<{
  history: ChatMessage[];
  messages: object[];
} | null> {
  try {
    const uid = getOrCreateAnonymousUid();
    const sessionsRef = collection(db, "users", uid, "sessions");
    const q = query(sessionsRef, orderBy("updatedAt", "desc"), limit(1));
    const snapshot = await getDocs(q);

    if (snapshot.empty) return null;

    const data = snapshot.docs[0].data();
    return {
      history: (data.history as ChatMessage[]) ?? [],
      messages: (data.messages as object[]) ?? [],
    };
  } catch {
    return null;
  }
}

/** Inicia uma nova sessão (novo UUID) — útil para "limpar" a conversa */
export function startNewSession(): void {
  localStorage.removeItem(SESSION_ID_KEY);
}
