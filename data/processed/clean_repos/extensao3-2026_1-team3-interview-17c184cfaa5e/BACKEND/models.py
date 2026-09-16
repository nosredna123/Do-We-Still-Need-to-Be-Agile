from enum import Enum

from pydantic import BaseModel, Field


class Recomendacao(str, Enum):
    aprovado = "Aprovado para entrevista"
    desenvolvimento = "Requer desenvolvimento"
    nao_recomendado = "Não recomendado"


class JobPosting(BaseModel):
    title: str
    description: str
    required_skills: list[str]
    experience_years: int


class AnalyzeRequest(BaseModel):
    job_id: str
    resume_text: str


class AnalysisResult(BaseModel):
    titulo_vaga: str
    habilidades_vaga: list[str]
    nivel_compatibilidade: int = Field(..., ge=0, le=100)
    pontos_fortes: list[str]
    pontos_fracos: list[str]
    habilidades_faltantes: list[str]
    recomendacao: Recomendacao
    resumo: str


class SecaoMelhoria(BaseModel):
    secao: str
    problemas: list[str]
    sugestoes: list[str]


class ResumeImprovementResult(BaseModel):
    pontuacao_geral: int = Field(..., ge=0, le=100)
    resumo_diagnostico: str
    melhorias_por_secao: list[SecaoMelhoria]
    habilidades_recomendadas: list[str]
    palavras_chave_faltantes: list[str]
    acoes_prioritarias: list[str]


class ImproveRequest(BaseModel):
    resume_text: str


class InterviewQuestionsRequest(BaseModel):
    titulo_vaga: str
    habilidades_vaga: list[str]
    pontos_fortes: list[str]
    pontos_fracos: list[str]
    habilidades_faltantes: list[str]
    nivel_compatibilidade: int = Field(..., ge=0, le=100)


class InterviewQuestionsResult(BaseModel):
    titulo_vaga: str
    total_perguntas: int
    perguntas: list[str]


class RelatedJob(BaseModel):
    titulo: str
    url: str
    descricao: str


class RelatedJobsRequest(BaseModel):
    titulo_vaga: str
    habilidades_vaga: list[str] = []


class RelatedJobsResult(BaseModel):
    titulo_vaga: str
    total: int
    vagas: list[RelatedJob]
