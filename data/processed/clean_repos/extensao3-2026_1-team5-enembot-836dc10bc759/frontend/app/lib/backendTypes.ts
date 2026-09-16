/** Tipos alinhados aos schemas do backend (routes_front). */

export type UserSchema = {
  id: number;
  username: string;
  email: string;
  password: string;
};

export type ChatSchema = {
  id: number;
  user_id: number;
  habilidade: number;
  chat_name: string;
  status: 0 | 1;
  criado_em: string;
  atualizado_em: string;
};

export type ChatMessageSchema = {
  id: number;
  chat_id: number;
  author: string;
  texto: string;
  timestamp: string;
  question_id: number | null;
  essay_id: number | null;
};

export type AlternativaSchema = {
  letra: string;
  texto: string;
};

export type QuestionSchema = {
  id: number;
  habilidade: number;
  competencia: number;
  enunciado: string;
  alternativas: AlternativaSchema[];
  resposta_correta: string;
  image: string | null;
  dificuldade: number;
};

export type EssaySchema = {
  id: number,
  theme: number,
  text: string
}

export type MessageResponse = { message: string };

export type ChatsResponse = { chats: ChatSchema[] };

export type MensagensResponse = { mensagens: ChatMessageSchema[] };
