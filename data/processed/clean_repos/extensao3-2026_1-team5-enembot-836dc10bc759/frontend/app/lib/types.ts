/**
 * Tipos de dominio compartilhados pela UI.
 * Alinhados (mas nao iguais) ao schema Supabase - a fronteira e a camada
 * lib/llm e lib/questionBank, que adaptam do banco para a UI.
 */

export type BuildId = 'estrategista' | 'teorico' | 'sniper';

export type SubjectId =
  | 'matematica'
  | 'linguagens'
  | 'natureza'
  | 'humanas'
  | 'redacao';

export type Difficulty = 'facil' | 'media' | 'dificil';

export type AlternativeLetter = 'A' | 'B' | 'C' | 'D' | 'E';

export type Alternative = {
  letra: AlternativeLetter;
  texto: string;
  correta: boolean;
  feedback?: string;
};

export type Question = {
  id: string;
  subjectId: SubjectId;
  assunto: string;
  ano?: number;
  dificuldade: Difficulty;
  enunciado: string;
  alternativas: Alternative[];
  explicacao: string;
};

export type Essay = {
  id: number,
  theme: number,
  text: string
}

export type ChatRole = 'user' | 'assistant' | 'system';

export type SmartSuggestion = {
  id: string;
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

export type ChatMessage = {
  id: string;
  role: ChatRole;
  /** Markdown com suporte a GFM + math ($...$) + <callout>...</callout> */
  content: string;
  /** Id da questao associada a essa mensagem, quando existir */
  questionId?: number;
  /** Quando a mensagem envolve uma questao */
  question?: Question;
  /** Letra escolhida pelo aluno (se aplicavel) */
  chosen?: AlternativeLetter;
  /** Quando a mensagem envolve uma redação */
  essayId?: number;
  /** Feedback apos resposta */
  feedback?: {
    correta: boolean;
    explicacao: string;
    fixacao?: string[];
  };
  /** Sugestoes contextuais apos resposta do bot */
  suggestions?: SmartSuggestion[];
  createdAt: number;
};

export type Subject = {
  id: SubjectId;
  title: string;
  description: string;
  icon: string;
  gradient: string;
  accent: string;
};

export type Build = {
  id: BuildId;
  icon: string;
  title: string;
  badge: string;
  description: string;
  /** Pitch que o bot apresenta ao iniciar sessao */
  systemPitch: string;
};
