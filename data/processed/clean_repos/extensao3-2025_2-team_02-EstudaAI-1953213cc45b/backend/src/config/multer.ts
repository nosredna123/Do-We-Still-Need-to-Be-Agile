import multer from "multer";

export const upload = multer({
  storage: multer.memoryStorage(), // mantém o arquivo em buffer (ideal para enviar para Supabase)
});
