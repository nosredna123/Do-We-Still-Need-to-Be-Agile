export type BodyFeeling =
  | "very_satisfied"
  | "satisfied"
  | "indifferent"
  | "dissatisfied"
  | "very_dissatisfied";

export type EatingStyle = "not" | "vegetarian" | "vegan";

/** Espelha o AnamneseSerializer do backend (1:1). */
export interface Anamnese {
  previous_consultation: boolean;
  previous_consultation_objective: string | null;
  previous_consultation_result: string | null;
  disease_history: string | null;
  medications: string | null;
  food_allergies: string | null;
  food_intolerances: string | null;
  favorite_foods: string;
  food_aversions: string | null;
  body_feeling: BodyFeeling | null;
  eating_style: EatingStyle;
  alcohol_intake: boolean;
  smoking: boolean;
}

export type AnamneseRequest = Anamnese;
