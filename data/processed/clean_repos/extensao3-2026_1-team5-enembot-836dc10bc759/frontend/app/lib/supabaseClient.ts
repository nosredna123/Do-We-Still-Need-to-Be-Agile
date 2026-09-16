import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import type { Database } from './database.types';

/**
 * Cliente Supabase singleton para uso no browser.
 *
 * As chaves vem de NEXT_PUBLIC_SUPABASE_URL e NEXT_PUBLIC_SUPABASE_ANON_KEY
 * (ver .env.local.example). Se as variaveis nao estiverem presentes o client
 * ainda e instanciado, mas qualquer chamada real falhara - o prototipo
 * continua funcionando pois toda a UI usa mocks nesta iteracao.
 */

const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? '';
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? '';

let _client: SupabaseClient<Database> | null = null;

export function getSupabaseClient(): SupabaseClient<Database> {
  if (_client) return _client;
  _client = createClient<Database>(url, anonKey, {
    auth: { persistSession: true, autoRefreshToken: true },
  });
  return _client;
}

export const isSupabaseConfigured = Boolean(url && anonKey);
