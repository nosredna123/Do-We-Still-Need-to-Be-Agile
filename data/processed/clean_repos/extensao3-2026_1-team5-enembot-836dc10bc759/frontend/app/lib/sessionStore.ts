import type { BuildId, SubjectId } from './types';

export type StoredSession = {
  id: string;
  subjectId: SubjectId;
  title: string;
  buildId?: BuildId;
  answered: number;
  correct: number;
  accuracy: number;
  updatedAt: number;
};

const RECENT_SESSIONS_KEY = 'enembot:recent_sessions';

function safeParse(value: string | null): StoredSession[] {
  if (!value) return [];
  try {
    const parsed = JSON.parse(value) as StoredSession[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function readSessions(): StoredSession[] {
  if (typeof window === 'undefined') return [];
  return safeParse(localStorage.getItem(RECENT_SESSIONS_KEY));
}

function writeSessions(sessions: StoredSession[]) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(RECENT_SESSIONS_KEY, JSON.stringify(sessions));
}

export function listRecentSessions(limit = 6): StoredSession[] {
  return readSessions()
    .sort((a, b) => b.updatedAt - a.updatedAt)
    .slice(0, limit);
}

export function upsertRecentSession(input: {
  id: string;
  subjectId: SubjectId;
  title: string;
  buildId?: BuildId;
  answered: number;
  correct: number;
}) {
  const now = Date.now();
  const accuracy = input.answered > 0 ? Math.round((input.correct / input.answered) * 100) : 0;
  const next: StoredSession = {
    id: input.id,
    subjectId: input.subjectId,
    title: input.title,
    buildId: input.buildId,
    answered: input.answered,
    correct: input.correct,
    accuracy,
    updatedAt: now,
  };

  const sessions = readSessions();
  const filtered = sessions.filter((session) => session.id !== input.id);
  writeSessions([next, ...filtered].slice(0, 20));
}

export function totalAnsweredInRecentSessions(): number {
  return readSessions().reduce((sum, session) => sum + (session.answered || 0), 0);
}

export function formatRecentLabel(updatedAt: number): string {
  const elapsed = Date.now() - updatedAt;
  const minute = 60_000;
  const hour = minute * 60;
  const day = hour * 24;
  if (elapsed < hour) return 'Hoje';
  if (elapsed < day) return 'Ontem';
  return `${Math.max(2, Math.round(elapsed / day))} dias`;
}
