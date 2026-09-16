import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Escopo: Permissão total de leitura/escrita na agenda
SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PICKLE = 'token.pickle'
CREDENTIALS_JSON = 'credentials.json'


def get_calendar_service():
    """
    Autentica com a API do Google Calendar e retorna um objeto de serviço.
    Manuseia o fluxo OAuth 2.0, abrindo um navegador para autorização
    na primeira vez que for executado.
    """
    creds = None

    # O arquivo token.pickle armazena os tokens de acesso do usuário.
    # Ele é criado automaticamente na primeira vez que a autorização é concluída.
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)

    # Se não houver credenciais (válidas), deixa o usuário fazer login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_JSON):
                print(f"ERRO: Arquivo '{CREDENTIALS_JSON}' não encontrado.")
                print("Por favor, siga as instruções para baixar o JSON de credenciais.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON, SCOPES)
            creds = flow.run_local_server(port=0)

        # Salva as credenciais para a próxima execução
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)

    # Constrói o objeto de serviço
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Erro ao construir o serviço do Google Calendar: {e}")
        return None