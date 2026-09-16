import { authRest } from "./rest/auth.rest";
import { tokenStorage } from "@/config/tokenStorage";
import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
} from "@/models/auth.model";

export const authService = {
  /** Cadastra o usuário e já realiza login para emitir os tokens (RF001). */
  registrar: async (body: RegisterRequest): Promise<LoginResponse> => {
    await authRest.register(body);
    return authService.login({ email: body.email, password: body.password });
  },

  login: async (body: LoginRequest): Promise<LoginResponse> => {
    const data = await authRest.login(body);
    tokenStorage.setTokens(data.access, data.refresh);
    tokenStorage.setUser(data.user);
    return data;
  },

  logout: async (): Promise<void> => {
    const refresh = tokenStorage.getRefresh();
    try {
      if (refresh) await authRest.logout(refresh);
    } finally {
      tokenStorage.clear();
    }
  },

  getMe: async (): Promise<AuthUser> => {
    const user = await authRest.getMe();
    tokenStorage.setUser(user);
    return user;
  },

  atualizarPerfil: async (
    body: Partial<{ username: string; password: string }>,
  ): Promise<AuthUser> => {
    const user = await authRest.updateMe(body);
    tokenStorage.setUser(user);
    return user;
  },
};
