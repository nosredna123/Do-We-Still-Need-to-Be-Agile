import type { AlternativeLetter, BuildId, Question, SubjectId } from '../types';

/**
 * CONTRATO do cliente LLM. Toda a UI depende APENAS desta interface.
 *
 * Ponto de troca: para integrar OpenAI de verdade, criar `openAiLlmClient.ts`
 * que implemente LlmClient, e trocar o import em
 * `frontend/app/lib/llm/index.ts`. Nada mais no app precisa mudar.
 */

export type StartSessionInput = {
  subjectId: SubjectId;
  build?: BuildId;
};

export type StartSessionOutput = {
  greeting: string;
  firstQuestion: Question;
};

export type AnswerInput = {
  question: Question;
  chosen: AlternativeLetter;
  build?: BuildId;
};

export type AnswerOutput = {
  feedback: string;
  correta: boolean;
  explicacao: string;
  /** sugestoes proativas de acao apos a resposta */
  suggestions: SmartSuggestion[];
};

export type NextQuestionInput = {
  subjectId: SubjectId;
  build?: BuildId;
  alreadyAskedIds: string[];
  /** 'facil' | 'media' | 'dificil' | 'auto' (respeita a build) */
  adaptiveHint?: 'facil' | 'media' | 'dificil' | 'auto';
};

export type NextQuestionOutput = {
  intro: string;
  question: Question | null;
};

export type FreeReplyInput = {
  userMessage: string;
  subjectId: SubjectId;
  build?: BuildId;
  lastQuestion?: Question;
};

export type FreeReplyOutput = {
  reply: string;
  suggestions?: SmartSuggestion[];
};

/* ---------------- Novas capacidades ---------------- */

export type SmartSuggestion = {
  id: string;
  /** id da intencao ("easier", "summary", "similar", "next", etc) */
  action:
    | 'easier'
    | 'harder'
    | 'similar'
    | 'summary'
    | 'explain-simple'
    | 'flashcards'
    | 'next'
    | 'hint'
    | 'quiz-topic';
  label: string;
  icon?: string;
};

export type HighlightAction = 'explicar' | 'aprofundar' | 'gerar-questao' | 'traduzir';

export type HighlightInput = {
  selectedText: string;
  action: HighlightAction;
  subjectId: SubjectId;
  build?: BuildId;
};

export type HighlightOutput = {
  title: string;
  body: string;
};

export type StudyPlanInput = {
  /** texto livre do usuario: "faltam 60 dias, foco em exatas" */
  goal: string;
  /** minutos por dia */
  minutesPerDay?: number;
  /** dias totais */
  days?: number;
};

export type StudyPlanDay = {
  day: string; // "Seg", "Ter"
  subjectId: SubjectId;
  topic: string;
  minutes: number;
  goal: string;
};

export type StudyPlanOutput = {
  title: string;
  overview: string;
  week: StudyPlanDay[];
};

export type SessionInsightsInput = {
  subjectId: SubjectId;
  stats: {
    answered: number;
    correct: number;
    streak?: number;
  };
  history?: Array<{ questionId: string; correct: boolean; topic: string; difficulty: string }>;
};

export type SessionInsightsOutput = {
  accuracy: number;
  streak: number;
  timeMinutes: number;
  strongTopics: Array<{ topic: string; accuracy: number }>;
  weakTopics: Array<{ topic: string; accuracy: number }>;
  nextAction: {
    type: 'review' | 'new-topic' | 'challenge';
    label: string;
    detail: string;
  };
};

export type ReviewQueueInput = {
  subjectId?: SubjectId;
};

export type ReviewItem = {
  id: string;
  subjectId: SubjectId;
  topic: string;
  dueLabel: string; // "Hoje", "Amanha", "em 3 dias"
  overdue: boolean;
  interval: string; // "1 dia", "3 dias", "7 dias"
};

export type ReviewQueueOutput = {
  dueToday: ReviewItem[];
  upcoming: ReviewItem[];
  summary: string;
};

export type CommandActionId =
  | 'generate-similar'
  | 'explain-eli5'
  | 'summarize-topic'
  | 'flashcards'
  | 'quiz-topic'
  | 'simulate-exam'
  | 'open-study-plan'
  | 'toggle-theme'
  | 'next-question'
  | 'give-hint'
  | 'switch-build'
  | 'start-focus-timer';

export type CommandActionInput = {
  actionId: CommandActionId;
  context?: {
    subjectId?: SubjectId;
    question?: Question;
    build?: BuildId;
  };
};

export type CommandActionOutput = {
  /** reply para stream do chat, se aplicavel */
  reply?: string;
  /** abrir modal? string identifier (study-plan, flashcards...) */
  openModal?: 'study-plan' | 'flashcards' | 'exam-sim';
  /** side-effect: e.g. trocar tema, mudar build */
  sideEffect?: { type: 'theme'; value: 'light' | 'dark' } | { type: 'build'; value: BuildId };
};

export interface LlmClient {
  startSession(input: StartSessionInput): Promise<StartSessionOutput>;
  answerQuestion(input: AnswerInput): Promise<AnswerOutput>;
  nextQuestion(input: NextQuestionInput): Promise<NextQuestionOutput>;
  freeReply(input: FreeReplyInput): Promise<FreeReplyOutput>;

  /* novos */
  highlight(input: HighlightInput): Promise<HighlightOutput>;
  buildStudyPlan(input: StudyPlanInput): Promise<StudyPlanOutput>;
  sessionInsights(input: SessionInsightsInput): Promise<SessionInsightsOutput>;
  reviewQueue(input: ReviewQueueInput): Promise<ReviewQueueOutput>;
  runCommand(input: CommandActionInput): Promise<CommandActionOutput>;
}
