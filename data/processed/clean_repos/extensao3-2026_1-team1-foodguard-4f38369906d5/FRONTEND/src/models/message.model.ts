import { type MessageRole } from "@/enums/MessageRole";
import type { IOpenFoodProduct } from "@/models/open-food.model";

export type Verdict =
  | "SAFE"
  | "LOW_CONCERN"
  | "MODERATE_RISK"
  | "HIGH_RISK"
  | "INSUFFICIENT_DATA";

export interface Message {
  chat_id: string;
  role: MessageRole;
  content: string;
  created_at: string;
  verdict: Verdict | null;
  recommends_doctor: boolean;
}

export interface MessageCreateRequest {
  role: MessageRole;
  content: string;
  chat_id?: string;
  /** Dados do produto escaneado (OpenFoodFacts) — alimenta a análise da IA. */
  food_data?: IOpenFoodProduct;
}

export interface MessageCreateResponse {
  chat_id: string;
  response: string;
  verdict: Verdict | null;
  recommends_doctor: boolean;
}
