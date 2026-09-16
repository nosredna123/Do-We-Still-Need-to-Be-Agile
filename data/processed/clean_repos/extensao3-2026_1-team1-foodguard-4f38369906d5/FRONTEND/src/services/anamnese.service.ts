import { anamneseRest } from "./rest/anamnese.rest";
import type { Anamnese, AnamneseRequest } from "@/models/anamnese.model";

export const anamneseService = {
  criar: (body: AnamneseRequest): Promise<Anamnese> => {
    return anamneseRest.create(body);
  },

  getMe: (): Promise<Anamnese> => {
    return anamneseRest.getMe();
  },

  atualizar: (body: Partial<AnamneseRequest>): Promise<Anamnese> => {
    return anamneseRest.update(body);
  },
};
