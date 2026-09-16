export interface ImproveRequest {
  resume_text: string;
  titulo_vaga: string;
  habilidades_vaga: string[];
  nivel_compatibilidade: number;
  pontos_fortes: string[];
  pontos_fracos: string[];
  habilidades_faltantes: string[];
  recomendacao: string;
  resumo: string;
}

export interface ImproveSection {
  secao: string;
  problemas: string[];
  sugestoes: string[];
}

export interface ImproveResponse {
  pontuacao_geral: number;
  resumo_diagnostico: string;
  melhorias_por_secao: ImproveSection[];
  habilidades_recomendadas: string[];
  palavras_chave_faltantes: string[];
  acoes_prioritarias: string[];
}