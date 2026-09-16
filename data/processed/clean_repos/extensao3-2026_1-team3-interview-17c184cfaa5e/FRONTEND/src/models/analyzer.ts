export interface AnalyzeResumeRequest {
  job_image: File;
  resume_pdf: File;
}

export interface AnalyzeResumeResponse {
  titulo_vaga: string;
  habilidades_vaga: string[];
  nivel_compatibilidade: number;
  pontos_fortes: string[];
  pontos_fracos: string[];
  habilidades_faltantes: string[];
  recomendacao: string;
  resumo: string;
}

