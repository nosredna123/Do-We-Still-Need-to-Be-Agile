import { retrieveQuestionById } from './backendApi';
import { findSubject } from './catalog';
import type { ChatMessageSchema, QuestionSchema, EssaySchema } from './backendTypes';
import { habilidadeNome, subjectToHabilidadeId } from './subjectHabilidade';
import type {
  Alternative,
  AlternativeLetter,
  ChatMessage,
  Difficulty,
  Essay,
  Question,
  SubjectId,
} from './types';

const ORDER: AlternativeLetter[] = ['A', 'B', 'C', 'D', 'E'];

export const NO_QUESTIONS_AVAILABLE =
  'Ainda não há questões disponíveis para esta matéria.';

export const NO_THEMES_AVAILABLE =
  'Ainda não há temas de redação disponíveis.';


function isQuestionStubText(text: string): boolean {
  return /^Questão #\d+ dispon[ií]vel abaixo\.?$/i.test(text.trim());
}

function difficultyFromInt(n: number): Difficulty {
  if (n <= 1) return 'facil';
  if (n >= 3) return 'dificil';
  return 'media';
}

function normalizeAlternativas(
  raw: QuestionSchema['alternativas'],
  correct: AlternativeLetter,
): Alternative[] {
  const list = (raw ?? [])
    .map((alt) => ({
      letra: (alt.letra?.trim().toUpperCase() ?? 'A') as AlternativeLetter,
      texto: (alt.texto ?? '').trim(),
      correta: alt.letra?.trim().toUpperCase() === correct,
    }))
    .filter((a) => a.texto.length > 0 && a.texto !== 'None');

  return ORDER.map((letra) => list.find((a) => a.letra === letra)).filter(
    (a): a is Alternative => Boolean(a),
  );
}

function matchesChatHabilidade(schema: QuestionSchema, chatSubjectId: SubjectId): boolean {
  return schema.habilidade === subjectToHabilidadeId(chatSubjectId);
}

async function fetchQuestionSchema(questionId: number): Promise<QuestionSchema | undefined> {
  try {
    return await retrieveQuestionById(questionId);
  } catch {
    return undefined;
  }
}

/** Chip do card = matéria do chat (URL). Só monta card se a questão for da mesma habilidade. */
export function mapQuestionSchema(q: QuestionSchema, chatSubjectId: SubjectId): Question {
  const correct = (q.resposta_correta?.trim().toUpperCase() ?? 'A') as AlternativeLetter;
  const alternativas = normalizeAlternativas(q.alternativas, correct);
  const subject = findSubject(chatSubjectId);

  return {
    id: String(q.id),
    subjectId: chatSubjectId,
    assunto: subject?.title ?? habilidadeNome(q.habilidade),
    dificuldade: difficultyFromInt(q.dificuldade ?? 2),
    enunciado: (q.enunciado ?? '').trim(),
    alternativas,
    explicacao: '',
  };
}

function mapRole(author: string): ChatMessage['role'] {
  if (author === 'user') return 'user';
  return 'assistant';
}

function parseTimestamp(ts: string): number {
  const n = Date.parse(ts);
  return Number.isNaN(n) ? Date.now() : n;
}

type CachedQuestion = { question: Question };

const questionCache = new Map<string, CachedQuestion>();

// Cache simples sem subjectId pois redações não têm matéria
const essayCache = new Map<number, Essay>();

function cacheKey(chatSubjectId: SubjectId, questionId: number) {
  return `${chatSubjectId}:${questionId}`;
}

export function clearQuestionCache() {
  questionCache.clear();
}

export async function loadQuestion(
  questionId: number,
  chatSubjectId: SubjectId,
): Promise<Question | undefined> {
  const key = cacheKey(chatSubjectId, questionId);
  if (questionCache.has(key)) return questionCache.get(key)?.question;

  const schema = await fetchQuestionSchema(questionId);
  if (!schema || !matchesChatHabilidade(schema, chatSubjectId)) return undefined;

  const q = mapQuestionSchema(schema, chatSubjectId);
  if (q.alternativas.length < 2) return undefined;
  questionCache.set(key, { question: q });
  return q;
}

/** Só a primeira mensagem do bot por question_id vira card. */
function presentationMessageIds(list: ChatMessageSchema[], chatSubjectId: SubjectId): Set<number> {
  const ids = new Set<number>();
  const seenQuestion = new Set<number>();

  for (const msg of list) {
    if (msg.author !== 'llm' || msg.question_id == null) continue;
    if (seenQuestion.has(msg.question_id)) continue;
    const cached = questionCache.get(cacheKey(chatSubjectId, msg.question_id));
    if (!cached || cached.question.alternativas.length < 2) continue;
    seenQuestion.add(msg.question_id);
    ids.add(msg.id);
  }

  return ids;
}

export function mapBackendMessage(msg: ChatMessageSchema, question?: Question): ChatMessage {
  const showCard = Boolean(question);
  let content = msg.texto;
  if (showCard) {
    content = '';
  } else if (
    msg.author === 'llm' &&
    msg.question_id != null &&
    isQuestionStubText(msg.texto)
  ) {
    content = NO_QUESTIONS_AVAILABLE;
  }
  return {
    id: String(msg.id),
    role: mapRole(msg.author),
    content,
    questionId: msg.question_id ?? undefined,
    question: showCard ? question : undefined,
    createdAt: parseTimestamp(msg.timestamp),
  };
}

export async function mapBackendMessages(
  msgs: ChatMessageSchema[] | null | undefined,
  subjectId: SubjectId,
): Promise<ChatMessage[]> {
  const list = Array.isArray(msgs) ? msgs : [];
  const questionIds = [
    ...new Set(list.map((m) => m.question_id).filter((id): id is number => id != null)),
  ];
  await Promise.all(questionIds.map((id) => loadQuestion(id, subjectId)));

  const cardMsgIds = presentationMessageIds(list, subjectId);

  return list.map((msg) => {
    let question: Question | undefined;
    if (cardMsgIds.has(msg.id) && msg.question_id != null) {
      question = questionCache.get(cacheKey(subjectId, msg.question_id))?.question;
    }
    return mapBackendMessage(msg, question);
  });
}

export function currentQuestionIdFromMessages(
  msgs: ChatMessageSchema[] | null | undefined,
  subjectId: SubjectId,
): number {
  const list = Array.isArray(msgs) ? msgs : [];
  const cardIds = presentationMessageIds(list, subjectId);

  for (let i = list.length - 1; i >= 0; i--) {
    const msg = list[i];
    if (cardIds.has(msg.id) && msg.question_id != null) return msg.question_id;
  }

  for (let i = list.length - 1; i >= 0; i--) {
    const id = list[i].question_id;
    if (id != null && questionCache.has(cacheKey(subjectId, id))) return id;
  }

  return 0;
}

/* Métodos de Redação */

export function mapBackendMessageEssay(msg: ChatMessageSchema, essayId?: number): ChatMessage {
  const showCard = essayId != null;
  let content = msg.texto;
  if (
    !showCard &&
    msg.author === 'llm' &&
    msg.essay_id != null &&
    isQuestionStubText(msg.texto)
  ) {
    content = NO_THEMES_AVAILABLE;
  }
  return {
    id: String(msg.id),
    role: mapRole(msg.author),
    content,
    essayId: showCard ? essayId : undefined,
    createdAt: parseTimestamp(msg.timestamp),
  };
}

function presentationEssayMessageIds(list: ChatMessageSchema[]): Set<number> {
  const ids = new Set<number>();
  const seenEssay = new Set<number>();

  for (const msg of list) {
    if (msg.author !== 'llm' || msg.essay_id == null) continue;
    if (seenEssay.has(msg.essay_id)) continue;
    seenEssay.add(msg.essay_id);
    ids.add(msg.id);
  }

  return ids;
}

export async function mapBackendMessagesEssay(
  msgs: ChatMessageSchema[] | null | undefined,
): Promise<ChatMessage[]> {
  const list = Array.isArray(msgs) ? msgs : [];
  const cardMsgIds = presentationEssayMessageIds(list);

  return list.map((msg) => {
    const isCard = cardMsgIds.has(msg.id) && msg.essay_id != null;
    return mapBackendMessageEssay(msg, isCard ? (msg.essay_id ?? undefined) : undefined);
  });
}