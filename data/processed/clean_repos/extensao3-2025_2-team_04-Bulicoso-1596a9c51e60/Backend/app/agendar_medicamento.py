import os
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import pytz  # <-- 1. NOVO IMPORT

load_dotenv(".env", override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("ERRO CRÍTICO: GOOGLE_API_KEY não encontrada no .env!")
    exit()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from google_calendar_auth import get_calendar_service


TZ_SAO_PAULO = pytz.timezone("America/Sao_Paulo")

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

prompt_template = PromptTemplate(
    input_variables=["instrucao"],
    template=PARSER_PROMPT
)


def parse_instruction(text: str) -> dict:
    """Usa o LLM para converter texto em um JSON estruturado."""
    try:
        # --- 2. MODELO ALTERADO ---
        llm_parser = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.5,
            google_api_key=GOOGLE_API_KEY
        )
    except Exception as e:
        print(f"[ERRO] Falha ao INICIALIZAR o Gemini: {e}")
        return None

    print(f"[LLM] Analisando instrução: '{text}'")
    prompt = prompt_template.format(instrucao=text)
    try:
        response = llm_parser.invoke(prompt)
        content = response.content
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            print("[ERRO] LLM não retornou um JSON válido.")
            return None
        clean_json = json_match.group(0)
        details = json.loads(clean_json)
        if "medicamento" not in details or "intervalo_horas" not in details or "duracao_dias" not in details:
            print("[ERRO] JSON retornado não contém as chaves necessárias.")
            return None
        print(f"[LLM] Dados extraídos: {details}")
        return details
    except Exception as e:
        print(f"[ERRO] Falha ao CHAMAR o LLM (invoke): {e}")
        return None

def get_user_start_time() -> datetime:
    """
    [MODIFICADO]
    Pede ao usuário um horário de início e o valida,
    forçando o fuso horário de São Paulo.
    """
    while True:
        try:
            start_str = input("Quando começar? (Ex: 'agora' ou '28/10/2025 08:30')\n> ")

            # --- 3. LÓGICA DE FUSO ALTERADA ---
            if start_str.lower() == 'agora' or start_str == "":
                # Retorna a hora atual JÁ no fuso de São Paulo
                return datetime.now(TZ_SAO_PAULO) + timedelta(minutes=1)

            # Tenta parsear o formato DD/MM/AAAA HH:MM (como um horário "ingênuo")
            naive_user_time = datetime.strptime(start_str, '%d/%m/%Y %H:%M')

            # Converte o horário "ingênuo" para um horário "consciente" no fuso de SP
            aware_user_time = TZ_SAO_PAULO.localize(naive_user_time)
            return aware_user_time

        except ValueError:
            print("Formato inválido. Por favor, use 'agora' ou 'DD/MM/AAAA HH:MM'.")


def create_calendar_events(service, details: dict, start_time: datetime, treatment_id: str):
    """Cria os eventos no Google Calendar."""

    medicamento = details["medicamento"]
    intervalo_horas = int(details["intervalo_horas"])
    duracao_dias = int(details["duracao_dias"])

    total_doses = (duracao_dias * 24) // intervalo_horas

    # O start_time já está no fuso correto (vindo de get_user_start_time)
    print(f"[CAL] Agendando {total_doses} doses de {medicamento}...")

    for i in range(total_doses):
        dose_time = start_time + timedelta(hours=(i * intervalo_horas))
        end_time = dose_time + timedelta(minutes=30)

        # --- 4. SEU CÓDIGO DE EVENT_BODY ---
        event_body = {
            'summary': f'Tomar {medicamento.upper()}',
            'description': f'Dose {i + 1} de {total_doses} do tratamento.\n\nID do Tratamento: {treatment_id}',
            'start': {
                'dateTime': dose_time.isoformat(),
                'timeZone': "America/Sao_Paulo",  # Força o fuso na API
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': "America/Sao_Paulo",  # Força o fuso na API
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 10},
                    {'method': 'email', 'minutes': 30},
                ],
            },
            'extendedProperties': {
                'private': {
                    'medication_treatment_id': treatment_id,
                    'medication_name': medicamento.upper()
                }
            }
        }
        # --- FIM DO SEU CÓDIGO ---

        try:
            event = service.events().insert(
                calendarId='primary',
                body=event_body
            ).execute()
            print(f"  -> Evento criado: {event.get('summary')} às {dose_time.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            print(f"[ERRO] Falha ao criar evento: {e}")

def handle_schedule_flow(service):
    """Cuida do fluxo completo de agendamento."""
    try:
        instrucao = input("\nDigite a prescrição (Ex: Dipirona de 8 em 8 horas por 5 dias):\n> ")
        if instrucao.lower() == 'sair':
            return

        details = parse_instruction(instrucao)
        if not details:
            return

        start_time = get_user_start_time()
        treatment_id = f"medsched_{uuid.uuid4().hex[:8]}"
        details['treatment_id'] = treatment_id

        create_calendar_events(service, details, start_time, treatment_id)
        print(f"\n[SUCESSO] Tratamento de {details['medicamento']} agendado!")
        print(f"ID do Tratamento (para referência): {treatment_id}")

    except Exception as e:
        print(f"[ERRO INESPERADO no Agendamento] {e}")


def handle_cancel_flow(service):
    """Cuida do fluxo completo de cancelamento."""
    try:
        med_name = input("\nQual o nome do medicamento que deseja cancelar?\n> ").upper()
        if not med_name:
            return

        print(f"Buscando eventos futuros para '{med_name}'...")

        # --- 5. LÓGICA DE FUSO ALTERADA ---
        # Define o início da busca como 'agora' no fuso de São Paulo
        now_iso = datetime.now(TZ_SAO_PAULO).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            q=f'Tomar {med_name}',  # Busca pelo título
            timeMin=now_iso,  # Apenas eventos futuros (no fuso correto)
            maxResults=250,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            print(f"Nenhum evento futuro encontrado para 'Tomar {med_name}'.")
            return

        print(f"Encontrados {len(events)} eventos futuros para '{med_name}':")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # Converte o horário ISO de volta para um objeto datetime para formatar
            event_time = datetime.fromisoformat(start)
            print(f"  - {event['summary']} em {event_time.strftime('%d/%m/%Y %H:%M')}")

        confirm = input("\nDeseja excluir TODOS esses eventos? [s/N]\n> ").lower()

        if confirm == 's' or confirm == 'sim':
            print("Excluindo eventos...")
            for event in events:
                try:
                    service.events().delete(
                        calendarId='primary',
                        eventId=event['id']
                    ).execute()
                    print(f"  - Evento {event['id']} excluído.")
                except Exception as e:
                    print(f"  - Falha ao excluir evento {event['id']}: {e}")
            print("\n[SUCESSO] Eventos cancelados.")
        else:
            print("Operação cancelada.")

    except Exception as e:
        print(f"[ERRO INESPERADO no Cancelamento] {e}")
if __name__ == "__main__":
    print("--- Agendador de Medicamentos v2.1 (Fuso SP) ---")

    print("[AUTH] Iniciando autenticação no Google Calendar...")
    service = get_calendar_service()

    if not service:
        print("[AUTH] Falha na autenticação do Calendar. Encerrando.")
    else:
        print("[AUTH] Autenticação do Calendar OK!")

        while True:
            print("\nO que você gostaria de fazer?")
            print("1. Agendar novo medicamento")
            print("2. Cancelar um tratamento agendado")
            print("3. Sair")

            choice = input("> ")

            if choice == '1':
                handle_schedule_flow(service)
            elif choice == '2':
                handle_cancel_flow(service)
            elif choice == '3':
                print("Encerrando...")
                break
            else:
                print("Opção inválida. Tente novamente.")