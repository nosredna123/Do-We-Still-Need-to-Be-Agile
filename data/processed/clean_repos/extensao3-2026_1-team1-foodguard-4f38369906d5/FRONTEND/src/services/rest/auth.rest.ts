import api from "@/config/api";
import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
} from "@/models/auth.model";

const baseUrl = "/auth";

export const authRest = {
  register: (body: RegisterRequest): Promise<AuthUser> => {
    return api.post(`${baseUrl}/register/`, body);
  },

  login: (body: LoginRequest): Promise<LoginResponse> => {
    return api.post(`${baseUrl}/login/`, body);
  },

  logout: (refresh: string): Promise<void> => {
    return api.post(`${baseUrl}/logout/`, { refresh });
  },

  getMe: (): Promise<AuthUser> => {
    return api.get(`${baseUrl}/me/`);
  },

  updateMe: (body: Partial<{ username: string; password: string }>): Promise<AuthUser> => {
    return api.patch(`${baseUrl}/me/`, body);
  },
};
