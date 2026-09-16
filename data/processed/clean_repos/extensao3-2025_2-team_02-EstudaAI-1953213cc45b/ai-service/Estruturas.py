from typing import Dict, Optional
from pydantic import BaseModel, Field

#A função desse módulo é separar as classes para validação de cada saída estruturada gerada pela llm
class Resumo(BaseModel):
        titulo: str
        conteudo: str

class Lembrete(BaseModel):
    titulo: str
    descricao: str
    data: str = ""

class SaidaResumo(BaseModel):
    resumo: Resumo
    lembretes: Dict[str, Lembrete] = {}

class StudyPlanTitle(BaseModel):
    title: str


class StudyPlanTopic(BaseModel):
    title: str
    orderIndex: int


class StudyPlanExpanded(BaseModel):
    topicTitle: str
    orderIndex: int
    justification: str


class StudyPlanComplementary(BaseModel):
    title: str
    description: str
    orderIndex: int


class StudyPlanChecklistItem(BaseModel):
    title: str
    orderIndex: int
    description: str


class SaidaPlanoDeEstudos(BaseModel):
    title: StudyPlanTitle
    topics: Dict[str, StudyPlanTopic]
    expandedTopics: Dict[str, StudyPlanExpanded]
    complementaryTopics: Dict[str, StudyPlanComplementary]
    checklist: Dict[str, StudyPlanChecklistItem]
