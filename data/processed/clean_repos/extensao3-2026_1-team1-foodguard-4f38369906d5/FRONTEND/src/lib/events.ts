/**
 * Eventos globais de UI desacoplados (window CustomEvent).
 *
 * Usados para comunicar entre componentes que não compartilham árvore de props
 * (ex.: o modal de perfil vive na Navbar, a lista de chats vive na página).
 */

/**
 * Disparado após a anamnese ser atualizada com sucesso.
 *
 * RN004: atualizar a anamnese invalida os chats antigos no backend; a lista de
 * conversas escuta este evento para recarregar e refletir a invalidação.
 */
export const ANAMNESE_UPDATED_EVENT = "foodguard:anamnese-updated";

/**
 * Disparado quando a sessão expira / o refresh falha (interceptor Axios).
 *
 * O AuthContext escuta este evento para limpar o estado de autenticação em
 * memória; as route guards então redirecionam para /login via React Router,
 * evitando um full page reload (window.location.assign).
 */
export const AUTH_LOGOUT_EVENT = "foodguard:auth-logout";
