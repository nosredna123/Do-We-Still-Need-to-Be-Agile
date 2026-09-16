import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { authService } from "@/services/auth.service";
import { tokenStorage } from "@/config/tokenStorage";
import { AUTH_LOGOUT_EVENT } from "@/lib/events";
import type {
  AuthUser,
  LoginRequest,
  RegisterRequest,
} from "@/models/auth.model";

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  hasAnamnese: boolean;
  login: (body: LoginRequest) => Promise<void>;
  register: (body: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  /** Atualiza o gate de anamnese após o usuário concluir o formulário (RN001). */
  markAnamneseDone: () => void;
  setUser: (user: AuthUser) => void;
}

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUserState] = useState<AuthUser | null>(() =>
    tokenStorage.getUser(),
  );
  const [hasAnamnese, setHasAnamnese] = useState<boolean>(
    () => tokenStorage.getUser()?.has_anamnese ?? false,
  );

  const persistUser = useCallback((next: AuthUser) => {
    tokenStorage.setUser(next);
    setUserState(next);
    setHasAnamnese(next.has_anamnese);
  }, []);

  const clearAuth = useCallback(() => {
    setUserState(null);
    setHasAnamnese(false);
  }, []);

  const login = useCallback(
    async (body: LoginRequest) => {
      const data = await authService.login(body);
      persistUser(data.user);
    },
    [persistUser],
  );

  const register = useCallback(
    async (body: RegisterRequest) => {
      const data = await authService.registrar(body);
      persistUser(data.user);
    },
    [persistUser],
  );

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch {
      // Mesmo que a invalidação no backend falhe, limpamos o estado local
      // (o storage já é limpo no finally do authService.logout).
    } finally {
      clearAuth();
    }
  }, [clearAuth]);

  useEffect(() => {
    window.addEventListener(AUTH_LOGOUT_EVENT, clearAuth);
    return () => window.removeEventListener(AUTH_LOGOUT_EVENT, clearAuth);
  }, [clearAuth]);

  const markAnamneseDone = useCallback(() => {
    setHasAnamnese(true);
    const current = tokenStorage.getUser();
    if (current) tokenStorage.setUser({ ...current, has_anamnese: true });
    setUserState((u) => (u ? { ...u, has_anamnese: true } : u));
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: !!user,
      hasAnamnese,
      login,
      register,
      logout,
      markAnamneseDone,
      setUser: persistUser,
    }),
    [user, hasAnamnese, login, register, logout, markAnamneseDone, persistUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
