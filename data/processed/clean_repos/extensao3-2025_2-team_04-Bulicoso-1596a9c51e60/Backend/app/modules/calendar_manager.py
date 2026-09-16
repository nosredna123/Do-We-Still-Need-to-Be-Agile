# modules/calendar_manager.py
import re
import json
import uuid
import pytz
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Configurações
TZ_SAO_PAULO = pytz.timezone("America/Sao_Paulo")

# Seu prompt parser
PARSER_PROMPT = """
Você é um assistente inteligente que extrai dados de prescrições médicas.
Analise a instrução do usuário e retorne APENAS um objeto JSON com 3 chaves:
1. "medicamento": (string) O nome do medicamento.
2. "intervalo_horas": (int) O intervalo em horas entre as doses.
3. "duracao_dias": (int) O número total de dias.
Instrução do Usuário:
{instrucao}
JSON:
"""
parser_prompt_template = PromptTemplate(
    input_variables=["instrucao"],
    template=PARSER_PROMPT
)


# Função helper para datas (para corrigir o bug do 'Z')
def parse_iso_datetime(dt_str: str) -> datetime:
    if dt_str.endswith('Z'):
        dt_str = dt_str[:-1] + '+00:00'
    return datetime.fromisoformat(dt_str)


# --- Funções do Parser ---
def parse_instruction(text: str, llm: ChatGoogleGenerativeAI) -> dict:
    """Usa o LLM (Parser) para converter texto em um JSON estruturado."""
    print(f"[Parser] Analisando instrução: '{text}'")
    prompt = parser_prompt_template.format(instrucao=text)
    try:
        response = llm.invoke(prompt)
        content = response.content
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            print("[Parser ERRO] LLM não retornou JSON.")
            return None

        clean_json = json_match.group(0)
        details = json.loads(clean_json)

        if "medicamento" not in details or "intervalo_horas" not in details or "duracao_dias" not in details:
            return None
        print(f"[Parser] Dados extraídos: {details}")
        return details
    except Exception as e:
        print(f"[Parser ERRO] Falha: {e}")
        return None


# --- Funções do Google Calendar ---

def get_start_time_from_string(start_str: str) -> datetime:
    """Valida e converte a string de data/hora de início."""
    try:
        if start_str.lower() == 'agora' or start_str == "":
            return datetime.now(TZ_SAO_PAULO) + timedelta(minutes=1)

        naive_user_time = datetime.strptime(start_str, '%d/%m/%Y %H:%M')
        aware_user_time = TZ_SAO_PAULO.localize(naive_user_time)

        if aware_user_time < datetime.now(TZ_SAO_PAULO):
            raise ValueError("Data de início no passado.")
        return aware_user_time
    except ValueError as e:
        print(f"[Calendar] Erro na data de início: {e}")
        return None


def create_calendar_events(service, details: dict, start_time: datetime) -> dict:
    """Cria os eventos no Google Calendar."""
    medicamento = details["medicamento"]
    intervalo_horas = int(details["intervalo_horas"])
    duracao_dias = int(details["duracao_dias"])
    total_doses = (duracao_dias * 24) // intervalo_horas
    treatment_id = f"medsched_{uuid.uuid4().hex[:8]}"

    print(f"[Calendar] Agendando {total_doses} doses de {medicamento}...")
    created_events = []

    for i in range(total_doses):
        dose_time = start_time + timedelta(hours=(i * intervalo_horas))
        end_time = dose_time + timedelta(minutes=30)

        event_body = {
            'summary': f'Tomar {medicamento.upper()}',
            'description': f'Dose {i + 1} de {total_doses} do tratamento.\n\nID do Tratamento: {treatment_id}',
            'start': {'dateTime': dose_time.isoformat(), 'timeZone': "America/Sao_Paulo"},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': "America/Sao_Paulo"},
            'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 10}]},
            'extendedProperties': {'private': {'treatment_id': treatment_id}}
        }
        try:
            event = service.events().insert(calendarId='primary', body=event_body).execute()
            created_events.append(event.get('id'))
        except Exception as e:
            print(f"[Calendar ERRO] Falha ao criar evento: {e}")

    return {
        "message": f"{len(created_events)} doses de {medicamento} agendadas.",
        "treatment_id": treatment_id,
        "total_doses": len(created_events)
    }


def find_future_events_by_name(service, med_name: str) -> list:
    """Busca e retorna eventos futuros na agenda pelo nome do medicamento."""
    print(f"[Calendar] Buscando eventos futuros para: '{med_name}'")
    now_iso = datetime.now(TZ_SAO_PAULO).isoformat()
    try:
        events_result = service.events().list(
            calendarId='primary', q=f'Tomar {med_name.upper()}', timeMin=now_iso,
            maxResults=250, singleEvents=True, orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        # Formatar para o frontend
        formatted_events = []
        for event in events:
            start_str = event['start'].get('dateTime', event['start'].get('date'))
            event_time = parse_iso_datetime(start_str)
            formatted_events.append({
                "id": event['id'],
                "summary": event['summary'],
                "start_time": event_time.isoformat(),
                "start_time_formatted": event_time.strftime('%d/%m/%Y %H:%M')
            })
        return formatted_events
    except Exception as e:
        print(f"[Calendar ERRO] Falha ao buscar eventos: {e}")
        return []


def delete_events(service, event_ids: list) -> dict:
    """Deleta uma lista de eventos (um ou 'todos')."""
    if not isinstance(event_ids, list):
        event_ids = [event_ids]  # Garante que seja uma lista

    print(f"[Calendar] Deletando {len(event_ids)} eventos...")
    deleted_count = 0
    errors = []
    for event_id in event_ids:
        try:
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            deleted_count += 1
        except Exception as e:
            print(f"[Calendar ERRO] Falha ao deletar {event_id}: {e}")
            errors.append(event_id)

    return {
        "message": f"{deleted_count} eventos deletados.",
        "deleted_count": deleted_count,
        "errors": errors
    }


def edit_single_event(service, event_id: str, new_start_str: str) -> dict:
    """Edita o horário de um único evento."""
    print(f"[Calendar] Editando evento {event_id} para {new_start_str}...")
    try:
        # Validar novo horário
        aware_new_time = get_start_time_from_string(new_start_str)
        if aware_new_time is None:
            return {"error": "Formato de data inválido. Use 'DD/MM/AAAA HH:MM' ou 'agora'."}

        # Obter o evento original para calcular a duração
        event = service.events().get(calendarId='primary', eventId=event_id).execute()

        original_start = parse_iso_datetime(event['start']['dateTime'])
        original_end = parse_iso_datetime(event['end']['dateTime'])
        duration = original_end - original_start

        aware_new_end_time = aware_new_time + duration

        # Preparar o corpo da atualização
        event['start'] = {'dateTime': aware_new_time.isoformat(), 'timeZone': "America/Sao_Paulo"}
        event['end'] = {'dateTime': aware_new_end_time.isoformat(), 'timeZone': "America/Sao_Paulo"}

        updated_event = service.events().update(
            calendarId='primary',
            eventId=event['id'],
            body=event
        ).execute()

        return {
            "message": "Evento atualizado com sucesso.",
            "id": updated_event.get('id'),
            "new_start_time": aware_new_time.isoformat()
        }

    except Exception as e:
        print(f"[Calendar ERRO] Falha ao atualizar evento: {e}")
        return {"error": str(e)}