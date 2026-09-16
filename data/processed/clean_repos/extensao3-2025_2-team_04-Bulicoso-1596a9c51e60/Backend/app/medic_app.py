import os
import json
import re
import uuid
import numpy as np
import pytz
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from google_calendar_auth import get_calendar_service

load_dotenv(".env", override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("ERRO CRÍTICO: GOOGLE_API_KEY não encontrada no .env!")
    exit()

# === CONFIGURAÇÕES GLOBAIS ===
TZ_SAO_PAULO = pytz.timezone("America/Sao_Paulo")
DB_DIR = "modules/chroma_bulas_local"
COLLECTION_NAME = "bulas_local"
MIN_CONFIDENCE_THRESHOLD = 0.6
RAG_TOP_K = 2

RAG_PROMPT_TEMPLATE = """
Você é um assistente especialista em bulas de medicamentos.
Responda à pergunta do usuário usando APENAS os trechos de contexto abaixo.

Contexto:
{context_chunks}

Pergunta:
{question}

Instruções para a resposta (formato JSON):

1.  **answer (string)**:
    * Extraia a resposta diretamente do contexto para responder à pergunta, pense e fale algo que faz sentido de acordo com o contexto.
    * **Se o contexto contiver qualquer informação relevante** (mesmo que parcial, como uma menção em 'Interações'), **apresente essa informação.**
    * Se o contexto não contiver NENHUMA informação relevante para a pergunta, responda EXATAMENTE: "NOT_FOUND"

2. **confidence**:
    * Quero o nível de confiança de 0 a 1.

Responda APENAS com o objeto JSON.
"""

FALLBACK_PROMPT_TEMPLATE = """
Você é um especialista em medicamentos. O banco de dados local não forneceu
informações confiáveis. Responda a pergunta abaixo usando seu
conhecimento geral.

Pergunta:
{question}

Instruções:
1. Responda a pergunta de forma clara e concisa.
2. AO FINAL da resposta, inclua o aviso: "Atenção: Esta informação foi gerada por IA e não substitui uma bula. Em caso de reações, procure um médico."
"""


def init_rag_db():
    """Carrega o ChromaDB e a função de embedding."""
    try:
        print("[RAG] Carregando modelo de embedding (HuggingFace)...")
        embedding_func = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("[RAG] Conectando ao banco de dados ChromaDB...")
        vectordb = Chroma(
            persist_directory=DB_DIR,
            collection_name=COLLECTION_NAME,
            embedding_function=embedding_func
        )
        print("[RAG] Banco de dados de bulas carregado.")
        return vectordb
    except Exception as e:
        print(f"[ERRO CRÍTICO RAG] Não foi possível carregar o ChromaDB: {e}")
        print("Verifique se a pasta 'chroma_bulas_local' existe e foi criada com o script de ingestão.")
        return None


def compute_confidence(scores):
    """Calcula a confiança com base nos scores de similaridade (distância)."""
    if not scores:
        return 0.0
    # Scores são 1.0 - distância
    return round(float(np.mean(scores)), 3)


def query_rag_reactions(medicamento_nome: str, vectordb: Chroma) -> str:
    """
    Executa o fluxo RAG completo (Busca, Fallback, Geração)
    para encontrar reações adversas.
    """
    print(f"[RAG] Buscando reações adversas para: {medicamento_nome}...")

    try:
        llm_rag = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Modelo atualizado
            temperature=0.5,
            google_api_key=GOOGLE_API_KEY
        )
    except Exception as e:
        return f"[ERRO RAG] Falha ao inicializar Gemini para RAG: {e}"

    query = f"Quais são as reações adversas da {medicamento_nome}?"

    docs_with_scores = vectordb.similarity_search_with_relevance_scores(
        query, k=RAG_TOP_K
    )

    context_blocks = []
    scores = []
    for d, score in docs_with_scores:
        similarity = 1.0 - score  # Chroma score é distância, convertendo para similaridade
        scores.append(similarity)
        context_blocks.append(d.page_content)

    retrieval_confidence = compute_confidence(scores)
    context_str = "\n\n---\n\n".join(context_blocks) if context_blocks else "NOT_FOUND"

    print(f"[RAG] Confiança da busca: {retrieval_confidence}")

    # 4. Lógica de Fallback
    if retrieval_confidence < MIN_CONFIDENCE_THRESHOLD or context_str == "NOT_FOUND":
        print("[RAG] Confiança baixa. Usando fallback (conhecimento geral do Gemini).")
        prompt_text = FALLBACK_PROMPT_TEMPLATE.format(question=query)
    else:
        print("[RAG] Confiança alta. Usando contexto do ChromaDB.")
        prompt_text = RAG_PROMPT_TEMPLATE.format(context_chunks=context_str, question=query)

    try:
        response = llm_rag.invoke(prompt_text)
        return response.content
    except Exception as e:
        return f"[ERRO RAG] Falha ao gerar resposta do Gemini: {e}"


PARSER_PROMPT = """
Você é um assistente inteligente que extrai dados de prescrições médicas.
Analise a instrução do usuário e retorne APENAS um objeto JSON com 3 chaves:
1. "medicamento": (string) O nome do medicamento.
2. "intervalo_horas": (int) O intervalo em horas entre as doses. Se for "1 vez ao dia", use 24.
3. "duracao_dias": (int) O número total de dias. Se for "uma semana", use 7.
Instrução do Usuário:
{instrucao}
JSON:
"""
parser_prompt_template = PromptTemplate(
    input_variables=["instrucao"],
    template=PARSER_PROMPT
)


def parse_instruction(text: str) -> dict:
    """Usa o LLM (Parser) para converter texto em um JSON estruturado."""
    try:
        # Inicializa o LLM aqui dentro para isolar a credencial
        llm_parser = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0,
            google_api_key=GOOGLE_API_KEY
        )
    except Exception as e:
        print(f"[ERRO PARSER] Falha ao INICIALIZAR o Gemini: {e}")
        return None

    print(f"[PARSER] Analisando instrução: '{text}'")
    prompt = parser_prompt_template.format(instrucao=text)
    try:
        response = llm_parser.invoke(prompt)
        content = response.content
        # Regex mais robusto para extrair o JSON
        json_match = re.search(r"```json\s*(\{.*?\})\s*```|(\{.*?\})", content, re.DOTALL)
        if not json_match:
            print("[ERRO PARSER] LLM não retornou um JSON válido.")
            return None

        # Pega o primeiro grupo que não for None (ou o JSON com ``` ou o JSON puro)
        clean_json = next(g for g in json_match.groups() if g is not None)

        details = json.loads(clean_json)
        if "medicamento" not in details or "intervalo_horas" not in details or "duracao_dias" not in details:
            print("[ERRO PARSER] JSON retornado não contém as chaves necessárias.")
            return None
        print(f"[PARSER] Dados extraídos: {details}")
        return details
    except json.JSONDecodeError as e:
        print(f"[ERRO PARSER] Falha ao decodificar JSON: {e}")
        print(f"Resposta bruta recebida: {content}")
        return None
    except Exception as e:
        print(f"[ERRO PARSER] Falha ao CHAMAR o LLM (invoke): {e}")
        return None


def get_user_start_time() -> datetime:
    """Pede ao usuário um horário de início e o valida (Fuso SP)."""
    while True:
        try:
            start_str = input("Quando começar? (Ex: 'agora' ou 'DD/MM/AAAA HH:MM' como 28/10/2025 08:30)\n> ")
            if start_str.lower() == 'agora' or start_str == "":
                # Adiciona 1 minuto para evitar agendar no passado imediato
                return datetime.now(TZ_SAO_PAULO) + timedelta(minutes=1)
            naive_user_time = datetime.strptime(start_str, '%d/%m/%Y %H:%M')
            aware_user_time = TZ_SAO_PAULO.localize(naive_user_time)

            if aware_user_time < datetime.now(TZ_SAO_PAULO):
                print("A data e hora de início não podem ser no passado. Tente novamente.")
                continue

            return aware_user_time
        except ValueError:
            print("Formato inválido. Por favor, use 'agora' ou 'DD/MM/AAAA HH:MM'.")


def create_calendar_events(service, details: dict, start_time: datetime, treatment_id: str):
    """Cria os eventos no Google Calendar."""
    medicamento = details["medicamento"]
    intervalo_horas = int(details["intervalo_horas"])
    duracao_dias = int(details["duracao_dias"])
    total_doses = (duracao_dias * 24) // intervalo_horas

    print(f"[CAL] Agendando {total_doses} doses de {medicamento}...")
    for i in range(total_doses):
        dose_time = start_time + timedelta(hours=(i * intervalo_horas))
        end_time = dose_time + timedelta(minutes=30)  # Duração padrão de 30 min

        # Garante que o nome do medicamento esteja em maiúsculas no título
        summary = f'Tomar {medicamento.upper()}'

        event_body = {
            'summary': summary,
            'description': f'Dose {i + 1} de {total_doses} do tratamento.\n\nID do Tratamento: {treatment_id}',
            'start': {'dateTime': dose_time.isoformat(), 'timeZone': "America/Sao_Paulo"},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': "America/Sao_Paulo"},
            'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 10}]},
            # Campo estendido para armazenar o ID do tratamento para facilitar a busca
            'extendedProperties': {
                'private': {
                    'treatment_id': treatment_id
                }
            }
        }
        try:
            event = service.events().insert(calendarId='primary', body=event_body).execute()
            print(f"  -> Evento criado: {event.get('summary')} às {dose_time.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            print(f"[ERRO CAL] Falha ao criar evento: {e}")


# --- FLUXO DE AGENDAMENTO ---
def handle_schedule_flow(calendar_service, rag_db):
    """FLUXO INTEGRADO: Agenda e depois busca no RAG."""
    try:
        instrucao = input("\nDigite a prescrição (Ex: Dipirona de 8 em 8 horas por 5 dias):\n> ")
        if instrucao.lower() == 'sair':
            return

        # --- PARTE 1: PARSER ---
        details = parse_instruction(instrucao)
        if not details:
            print("[ERRO] Não foi possível entender a prescrição.")
            return

        # --- PARTE 2: AGENDAMENTO ---
        start_time = get_user_start_time()
        treatment_id = f"medsched_{uuid.uuid4().hex[:8]}"
        details['treatment_id'] = treatment_id

        create_calendar_events(calendar_service, details, start_time, treatment_id)
        print(f"\n[SUCESSO] Tratamento de {details['medicamento']} agendado!")
        print(f"ID do Tratamento (para referência): {treatment_id}")

        # --- PARTE 3: RAG (A INTEGRAÇÃO) ---
        print("\n" + "=" * 40)
        print("BUSCANDO INFORMAÇÕES ADICIONAIS (RAG)...")
        rag_response = query_rag_reactions(details["medicamento"], rag_db)

        print("\n--- INFORMAÇÕES SOBRE REAÇÕES ADVERSAS ---")
        print(rag_response)
        print("=" * 40)

    except Exception as e:
        print(f"[ERRO INESPERADO no Agendamento] {e}")


# --- FUNÇÃO AUXILIAR PARA BUSCA ---
def find_future_events_by_name(service, med_name: str):
    """Busca e retorna eventos futuros na agenda pelo nome do medicamento."""
    print(f"Buscando eventos futuros para '{med_name}'...")
    now_iso = datetime.now(TZ_SAO_PAULO).isoformat()

    # A query 'q' busca pelo nome do medicamento no título do evento
    events_result = service.events().list(
        calendarId='primary', q=f'Tomar {med_name.upper()}', timeMin=now_iso,
        maxResults=250, singleEvents=True, orderBy='startTime'
    ).execute()

    return events_result.get('items', [])


# --- FLUXO DE CANCELAMENTO ---
# --- FLUXO DE CANCELAMENTO (ATUALIZADO) ---
def handle_cancel_flow(service):
    """
    Cuida do fluxo de cancelamento, permitindo cancelar um
    único evento ou o tratamento inteiro.
    """
    try:
        med_name = input("\nQual o nome do medicamento que deseja CANCELAR?\n> ")
        if not med_name:
            return

        events = find_future_events_by_name(service, med_name)

        if not events:
            print(f"Nenhum evento futuro encontrado para 'Tomar {med_name.upper()}'.")
            return

        print(f"\nEncontrados {len(events)} eventos futuros para '{med_name.upper()}':")
        # 1. Lista os eventos numerados
        for i, event in enumerate(events, 1):  # Começa a contagem do 1
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_time = datetime.fromisoformat(start)
            print(f"  {i}. {event['summary']} em {event_time.strftime('%d/%m/%Y %H:%M')}")

        # 2. Pergunta se quer cancelar um número ou 'todos'
        print("\nO que você deseja cancelar?")
        choice = input("Digite o NÚMERO do evento (ex: '1') ou 'todos' para cancelar o tratamento inteiro:\n> ").lower()

        if choice == 'todos':
            # Lógica antiga para apagar tudo
            print("Excluindo TODOS os eventos futuros...")
            delete_count = 0
            for event in events:
                try:
                    service.events().delete(calendarId='primary', eventId=event['id']).execute()
                    delete_count += 1
                except Exception as e:
                    print(f"  - Falha ao excluir evento {event['id']}: {e}")
            print(f"\n[SUCESSO] {delete_count} eventos cancelados.")

        elif choice.isdigit():
            # 3. Lógica NOVA para apagar um único evento
            try:
                index = int(choice)
                if 1 <= index <= len(events):
                    event_to_delete = events[index - 1]  # Ajusta para índice 0
                    event_id = event_to_delete['id']
                    start_time_str = datetime.fromisoformat(event_to_delete['start']['dateTime']).strftime(
                        '%d/%m/%Y %H:%M')

                    print(f"\nExcluindo evento: {event_to_delete['summary']} de {start_time_str}...")

                    # Chama a API para deletar o evento específico
                    service.events().delete(calendarId='primary', eventId=event_id).execute()

                    print("[SUCESSO] Evento cancelado.")
                else:
                    print("Número inválido. Fora do intervalo da lista.")
            except Exception as e:
                print(f"  - Falha ao excluir evento: {e}")
        else:
            print("Opção inválida. Operação cancelada.")

    except Exception as e:
        print(f"[ERRO INESPERADO no Cancelamento] {e}")



# --- NOVOS FLUXOS DE EDIÇÃO ---

def edit_single_event(service, event: dict):
    """Edita o horário de um único evento."""
    print(f"\nEditando evento: {event['summary']}")
    print(f"Horário atual: {datetime.fromisoformat(event['start']['dateTime']).strftime('%d/%m/%Y %H:%M')}")

    while True:
        try:
            new_start_str = input("Digite o NOVO dia e horário (DD/MM/AAAA HH:MM):\n> ")
            naive_new_time = datetime.strptime(new_start_str, '%d/%m/%Y %H:%M')
            aware_new_time = TZ_SAO_PAULO.localize(naive_new_time)

            if aware_new_time < datetime.now(TZ_SAO_PAULO):
                print("A data e hora não podem ser no passado. Tente novamente.")
                continue

            # Calcula o novo horário de término (mantendo a duração original do evento)
            original_start = datetime.fromisoformat(event['start']['dateTime'])
            original_end = datetime.fromisoformat(event['end']['dateTime'])
            duration = original_end - original_start

            aware_new_end_time = aware_new_time + duration

            # Prepara o corpo da atualização
            # O 'body' do update deve conter os campos que queremos alterar
            updated_event_body = {
                'summary': event['summary'],  # Mantém o mesmo resumo
                'description': event.get('description', ''),  # Mantém a mesma descrição
                'start': {'dateTime': aware_new_time.isoformat(), 'timeZone': "America/Sao_Paulo"},
                'end': {'dateTime': aware_new_end_time.isoformat(), 'timeZone': "America/Sao_Paulo"},
                'reminders': event.get('reminders',
                                       {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 10}]}),
                'extendedProperties': event.get('extendedProperties', {})  # Mantém propriedades
            }

            service.events().update(
                calendarId='primary',
                eventId=event['id'],
                body=updated_event_body
            ).execute()

            print("\n[SUCESSO] Evento atualizado com sucesso!")
            print(f"Novo horário: {aware_new_time.strftime('%d/%m/%Y %H:%M')}")
            break  # Sai do loop while

        except ValueError:
            print("Formato inválido. Por favor, use 'DD/MM/AAAA HH:MM'.")
        except Exception as e:
            print(f"[ERRO CAL] Falha ao atualizar evento: {e}")
            break  # Sai do loop em caso de erro da API


def edit_entire_treatment(service, events: list):
    """Substitui um tratamento inteiro (apaga antigos, cria novos)."""
    print(f"\nVocê irá substituir {len(events)} eventos futuros.")

    # 1. Pegar a nova prescrição
    instrucao = input("Digite a NOVA prescrição (Ex: Losartana de 12 em 12 horas por 10 dias):\n> ")
    new_details = parse_instruction(instrucao)
    if not new_details:
        print("[ERRO] Não foi possível entender a nova prescrição. Operação cancelada.")
        return

    # 2. Pegar o novo horário de início
    new_start_time = get_user_start_time()
    new_treatment_id = f"medsched_{uuid.uuid4().hex[:8]}"  # ID novo para o novo tratamento
    new_details['treatment_id'] = new_treatment_id

    # 3. Excluir os eventos antigos
    print("\nExcluindo tratamento antigo...")
    delete_count = 0
    for event in events:
        try:
            service.events().delete(calendarId='primary', eventId=event['id']).execute()
            delete_count += 1
        except Exception as e:
            print(f"  - Falha ao excluir evento {event['id']}: {e}")
    print(f"{delete_count} de {len(events)} eventos antigos excluídos.")

    # 4. Criar os novos eventos
    print("\nCriando novo tratamento agendado...")
    create_calendar_events(service, new_details, new_start_time, new_treatment_id)

    print("\n[SUCESSO] Tratamento atualizado com sucesso!")
    print(f"ID do Novo Tratamento (para referência): {new_treatment_id}")


def handle_edit_flow(service):
    """FLUXO DE EDIÇÃO: Permite editar um evento ou o tratamento inteiro."""
    try:
        med_name = input("\nQual o nome do medicamento que deseja EDITAR?\n> ")
        if not med_name:
            return

        events = find_future_events_by_name(service, med_name)

        if not events:
            print(f"Nenhum evento futuro encontrado para 'Tomar {med_name.upper()}'.")
            return

        print(f"\nEncontrados {len(events)} eventos futuros para '{med_name.upper()}':")
        for i, event in enumerate(events, 1):  # Começa a contagem do 1
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_time = datetime.fromisoformat(start)
            print(f"  {i}. {event['summary']} em {event_time.strftime('%d/%m/%Y %H:%M')}")

        print("\nO que você deseja editar?")
        choice = input("Digite o NÚMERO do evento (ex: '1') ou 'todos' para alterar o tratamento inteiro:\n> ").lower()

        if choice == 'todos':
            edit_entire_treatment(service, events)

        elif choice.isdigit():
            try:
                index = int(choice)
                if 1 <= index <= len(events):
                    event_to_edit = events[index - 1]  # Ajusta para índice 0
                    edit_single_event(service, event_to_edit)
                else:
                    print("Número inválido. Fora do intervalo da lista.")
            except ValueError:
                print("Entrada inválida. Digite um número ou 'todos'.")
        else:
            print("Opção inválida. Operação cancelada.")

    except Exception as e:
        print(f"[ERRO INESPERADO na Edição] {e}")


# --- FUNÇÃO PRINCIPAL ---

if __name__ == "__main__":
    print("--- Assistente de Agendamento e RAG v4.0 (Com Edição) ---")

    # 1. Autenticar no Calendar
    print("[AUTH] Iniciando autenticação no Google Calendar...")
    calendar_service = get_calendar_service()
    if not calendar_service:
        print("[AUTH] Falha na autenticação do Calendar. Encerrando.")
        exit()
    print("[AUTH] Autenticação do Calendar OK!")

    # 2. Carregar o Banco RAG
    rag_db = init_rag_db()
    if not rag_db:
        print("[RAG] Falha ao carregar banco de dados de bulas. Encerrando.")
        exit()

    print("\n--- Serviços Prontos ---")

    # 3. Iniciar Menu
    while True:
        print("\nO que você gostaria de fazer?")
        print("1. Agendar novo medicamento (e ver reações)")
        print("2. Cancelar um tratamento agendado")
        print("3. Editar um tratamento agendado")  # NOVA OPÇÃO
        print("4. Sair")  # OPÇÃO ANTIGA '3' ATUALIZADA

        choice = input("> ")

        if choice == '1':
            handle_schedule_flow(calendar_service, rag_db)
        elif choice == '2':
            handle_cancel_flow(calendar_service)
        elif choice == '3':
            handle_edit_flow(calendar_service)  # CHAMA O NOVO FLUXO
        elif choice == '4':
            print("Encerrando...")
            break
        else:
            print("Opção inválida. Tente novamente.")