import type { Verdict } from "@/models/message.model";

export interface Chat {
  id: string;
  title: string | null;
  created_at: string;
  is_active: boolean;
  /** Chat aberto (pode receber mensagens). False = fechado pela anamnese (só leitura). */
  is_open: boolean;
  /** URL da imagem do produto (OpenFoodFacts) exibida no card da galeria. */
  image_url: string | null;
  /** Severidade da conversa: veredito da avaliação mais recente. Null sem avaliação. */
  severity: Verdict | null;
  /** URL (HyperlinkedIdentityField) para o endpoint de mensagens deste chat. */
  messages: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
