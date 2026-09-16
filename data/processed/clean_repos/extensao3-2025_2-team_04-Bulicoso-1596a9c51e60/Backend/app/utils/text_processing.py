"""
🔹 PROCESSAMENTO DE TEXTO - Funções auxiliares

Este módulo contém funções auxiliares para processamento de texto:

1. Limpeza e normalização de texto
2. Detecção de idioma
3. Remoção de caracteres especiais
4. Normalização de nomes de medicamentos

IMPLEMENTAÇÃO NECESSÁRIA:
- Implementar funções de limpeza
- Normalização de texto
- Detecção de idioma (se necessário)
"""

import re
from typing import Optional
from app.core.logger import setup_logger

logger = setup_logger()


def clean_text(text: str) -> str:
    """
    🔹 IMPLEMENTAR: Limpa e normaliza texto de bula.
    
    Remove caracteres especiais, normaliza espaços,
    remove quebras de linha excessivas, etc.
    
    Args:
        text: Texto a ser limpo
        
    Returns:
        Texto limpo e normalizado
    """
    if not text:
        return ""
    
    # TODO: Implementar limpeza
    # - Remover caracteres especiais desnecessários
    # - Normalizar espaços múltiplos
    # - Remover quebras de linha excessivas
    # - Normalizar encoding
    
    # Exemplo básico:
    text = re.sub(r'\s+', ' ', text)  # Múltiplos espaços -> um espaço
    text = text.strip()
    
    return text


def normalize_medication_name(name: str) -> str:
    """
    🔹 IMPLEMENTAR: Normaliza nome de medicamento para busca.
    
    Remove acentos, converte para minúsculas, remove espaços extras.
    
    Args:
        name: Nome do medicamento
        
    Returns:
        Nome normalizado
    """
    if not name:
        return ""
    
    # TODO: Implementar normalização completa
    # - Converter para minúsculas
    # - Remover acentos
    # - Remover espaços extras
    # - Padronizar formato
    
    normalized = name.lower().strip()
    
    # Remover acentos (exemplo básico)
    # Para implementação completa, usar unidecode ou similar
    # from unidecode import unidecode
    # normalized = unidecode(normalized)
    
    return normalized


def extract_key_sections(text: str) -> dict:
    """
    🔹 IMPLEMENTAR: Extrai seções importantes de uma bula.
    
    Identifica e extrai seções como:
    - Indicações
    - Posologia
    - Contraindicações
    - Efeitos colaterais
    - Cuidados
    
    Args:
        text: Texto completo da bula
        
    Returns:
        Dicionário com seções extraídas
    """
    sections = {
        "indications": "",
        "dosage": "",
        "contraindications": "",
        "side_effects": "",
        "precautions": ""
    }
    
    # TODO: Implementar extração de seções
    # Usar regex ou NLP para identificar seções
    # patterns = {
    #     "indications": r"(?i)indica[çc][õo]es?|para que serve",
    #     "dosage": r"(?i)posologia|como tomar|dosagem",
    #     ...
    # }
    
    return sections


def detect_language(text: str) -> Optional[str]:
    """
    🔹 IMPLEMENTAR: Detecta idioma do texto.
    
    Args:
        text: Texto a analisar
        
    Returns:
        Código do idioma (pt, en, etc.) ou None
    """
    # TODO: Implementar detecção de idioma
    # Pode usar bibliotecas como langdetect
    
    # Por padrão, assumir português
    return "pt"


def remove_html_tags(text: str) -> str:
    """
    Remove tags HTML do texto.
    
    Args:
        text: Texto com HTML
        
    Returns:
        Texto sem tags HTML
    """
    # TODO: Usar BeautifulSoup ou regex para remover tags
    # from bs4 import BeautifulSoup
    # soup = BeautifulSoup(text, 'html.parser')
    # return soup.get_text()
    
    # Regex básico
    text = re.sub(r'<[^>]+>', '', text)
    return text

