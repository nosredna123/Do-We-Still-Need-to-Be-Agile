declare global {
  interface Lembrete {
    titulo: string;
    descricao: string;
    data?: Date;
  }

  interface Resumo {
    titulo: string;
    conteudo: string;
  }

  interface ResumosLembretesIA {
    resumo: Resumo;
    lembretes?: Record<string, Lembrete>;
  }

  interface StudyPlanTitle {
    title: string
  }

  interface StudyPlanTopic {
    title: string,
    orderIndex: number
  }

  interface StudyPlanExpanded {
    topicTitle: string,
    orderIndex: number,
    justification: string
  }

  interface StudyPlanComplementary {
    title: string,
    description: string,
    orderIndex: number
  }

  interface StudyPlanChecklistItem {
    title: string,
    orderIndex: number,
    description: string
  }

  interface StudyPlanResponse {
    title: StudyPlanTitle,
    topics: Record<string, StudyPlanTopic>,
    expandedTopics: Record<string, StudyPlanExpanded>,
    complementaryTopics: Record<string, StudyPlanComplementary>,
    checklist: Record<string, StudyPlanChecklistItem>
  }

  interface TranscriptResponse {
    filename: string,
    material_id: number,
    transcription: string
  }
}

export {}; // necessário para que o arquivo seja tratado como um módulo
