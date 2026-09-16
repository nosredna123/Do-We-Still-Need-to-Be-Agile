import pg from "pg";
import { registerType } from "pgvector/pg"; // API correta e atual

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  // Para Supabase local:
  // ssl: { rejectUnauthorized: false }
});

// Registrar o type vector para o PostgreSQL client
pool.on("connect", (client) => {
  registerType(client);
});

export { pool };