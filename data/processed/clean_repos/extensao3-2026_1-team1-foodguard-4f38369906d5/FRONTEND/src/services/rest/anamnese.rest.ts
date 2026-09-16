import api from "@/config/api";
import type { Anamnese, AnamneseRequest } from "@/models/anamnese.model";

const baseUrl = "/anamnese";

export const anamneseRest = {
  create: (body: AnamneseRequest): Promise<Anamnese> => {
    return api.post(`${baseUrl}/`, body);
  },

  getMe: (): Promise<Anamnese> => {
    return api.get(`${baseUrl}/me/`);
  },

  update: (body: Partial<AnamneseRequest>): Promise<Anamnese> => {
    return api.patch(`${baseUrl}/me/`, body);
  },
};
