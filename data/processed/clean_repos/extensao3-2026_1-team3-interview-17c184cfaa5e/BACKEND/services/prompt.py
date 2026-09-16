  
def build_compatibility_system_prompt() -> str:
    """System prompt para análise de compatibilidade via messages API."""
    return (
        "Você é um recrutador sênior experiente. "
        "Responda SOMENTE com JSON válido e completo. "
        "Use APENAS informações presentes nos textos fornecidos. "
        "NUNCA invente ou suponha informações. "
        "Se não houver informação suficiente, coloque lista vazia []."
    )
 
 
def build_interview_system_prompt() -> str:
    """System prompt para geração de perguntas de entrevista."""
    return (
        "Você é um especialista em recrutamento e seleção. "
        "Responda SOMENTE com JSON válido e completo. "
        "Gere perguntas relevantes baseadas no perfil e na vaga. "
        "NUNCA repita perguntas. "
        "As perguntas devem ser em português do Brasil."
    )
def build_improvement_system_prompt() -> str:
    """System prompt para análise e melhoria de currículo."""
    return (
        "Você é um especialista em RH e carreira. "
        "Responda SOMENTE com JSON válido e completo. "
        "Use APENAS informações presentes no currículo fornecido. "
        "NUNCA invente ou suponha informações. "
        "Se não houver informação suficiente, coloque lista vazia []."
    )