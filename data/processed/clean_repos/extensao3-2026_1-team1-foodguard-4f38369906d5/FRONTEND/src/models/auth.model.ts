export interface AuthUser {
  id: string;
  name: string;
  username: string;
  email: string;
  date_of_birth: string | null;
  has_anamnese: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  username: string;
  email: string;
  date_of_birth: string | null;
  password: string;
  password_confirm: string;
}

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface LoginResponse extends TokenPair {
  has_anamnese: boolean;
  user: AuthUser;
}
