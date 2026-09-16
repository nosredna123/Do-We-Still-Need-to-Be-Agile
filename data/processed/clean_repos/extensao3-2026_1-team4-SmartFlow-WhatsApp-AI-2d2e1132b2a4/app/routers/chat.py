from fastapi import APIRouter, status
from pydantic import BaseModel
from app.database.manipulations import ia_manipulations
from app.service.llm_response import IAresponse

router = APIRouter(prefix="/api", tags=["chat"])

class ChatMessage(BaseModel):
    message: str
    ia_id: int
    history: list = []

@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat_endpoint(data: ChatMessage):
    """
    Endpoint para processar mensagens de chat da interface web
    Recebe: {"message": "texto", "ia_id": 1, "history": []}
    Retorna: {"response": "resposta da IA", "success": true/false}
    """
    try:
        user_message = data.message.strip()
        ia_id = data.ia_id
        history = data.history or []
        
        print(f"\n{'='*60}")
        print(f"[CHAT] Recebido: message={user_message[:50]}... ia_id={ia_id}")
        
        if not user_message:
            return {"success": False, "error": "Mensagem vazia", "response": ""}
        
        # Buscar IA
        print(f"[CHAT] Buscando IA com ID {ia_id}...")
        ia_infos = ia_manipulations.filter_ia_by_id(ia_id)
        if not ia_infos:
            print(f"[CHAT] [ERRO] IA não encontrada com ID {ia_id}")
            return {"success": False, "error": f"IA não encontrada (ID: {ia_id}). Crie uma IA primeiro.", "response": ""}
        
        print(f"[CHAT] [OK] IA encontrada: {ia_infos.name}")
        
        if not ia_infos.status:
            print(f"[CHAT] [ERRO] IA {ia_infos.name} está desativada")
            return {"success": False, "error": f"IA {ia_infos.name} está desativada", "response": ""}
        
        # Verificar se tem prompt ativo
        system_prompt = ia_infos.active_prompt
        if not system_prompt:
            print(f"[CHAT] [ERRO] Nenhum prompt ativo para IA {ia_infos.name}")
            return {"success": False, "error": f"Nenhum prompt ativo para {ia_infos.name}. Crie e ative um prompt.", "response": ""}
        
        print(f"[CHAT] [OK] Prompt ativo encontrado")
        
        # Verificar config
        if not ia_infos.ia_config:
            print(f"[CHAT] [ERRO] Nenhuma configuração para IA {ia_infos.name}")
            return {"success": False, "error": f"Configure a IA {ia_infos.name} com uma API key.", "response": ""}
        
        # Extrair credenciais
        api_key = ia_infos.ia_config.credentials.get("api_key")
        ia_model = ia_infos.ia_config.credentials.get("ai_model", "gpt-4o-mini")
        
        if not api_key:
            print(f"[CHAT] [ERRO] Nenhuma API key configurada para {ia_infos.name}")
            return {"success": False, "error": f"IA {ia_infos.name} não tem API key. Configure em Settings.", "response": ""}
        
        print(f"[CHAT] [OK] API key configurada. Model: {ia_model}")
        print(f"[CHAT] [OK] API key primeiros 20 chars: {api_key[:20]}...")
        
        # Gerar resposta com LLM
        print(f"[CHAT] Inicializando LLM...")
        try:
            llm = IAresponse(
                api_key=api_key,
                ia_model=ia_model,
                system_prompt=system_prompt.prompt_text,
                resume_lead="",
                bot_id=ia_id  # Sem knowledge base ainda, usar None
            )
            
            print(f"[CHAT] LLM inicializado. Enviando mensagem para processamento...")
            print(f"[CHAT] Historico de mensagens: {len(history)} mensagens")
            
            # Converter histórico para formato esperado pelo LLM
            response = llm.generate_response(
                bot_id=ia_id,  # Sem knowledge base ainda, usar None
                message_lead=user_message,
                history_message=history
            )

            if not response and getattr(llm, "last_error", ""):
                error_detail = getattr(llm, "last_error", "")
                print(f"[CHAT] [ERRO] Detalhe do LLM: {error_detail}")
                return {"success": False, "error": f"Erro no LLM: {error_detail}", "response": ""}
            
            print(f"[CHAT] Response bruto do LLM: {response}")
            print(f"[CHAT] Tipo da response: {type(response)}")
            
            if not response:
                print(f"[CHAT] [ERRO] LLM retornou resposta vazia/None")
                return {"success": False, "error": "LLM não gerou resposta. Verifique a API key e model.", "response": ""}
            
            # Se for lista, extrair texto
            if isinstance(response, list):
                print(f"[CHAT] Response e lista com {len(response)} itens")
                response = next((item['text'] for item in response if 'text' in item), "")
            
            if not response or response.strip() == "":
                print(f"[CHAT] [ERRO] Resposta vazia apos processamento")
                return {"success": False, "error": "Resposta vazia do LLM. Tente novamente.", "response": ""}
            
            print(f"[CHAT] [OK] Resposta gerada com sucesso")
            print(f"[CHAT] Conteudo: {response[:100]}...")
            print(f"{'='*60}\n")
            
            return {
                "success": True,
                "response": response,
                "ia_name": ia_infos.name,
                "error": None
            }
        
        except Exception as llm_error:
            error_str = str(llm_error)
            print(f"[CHAT] [ERRO] ERRO NO LLM: {error_str}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            
            # Detecta erro de quota do OpenAI
            if "insufficient_quota" in error_str or "429" in error_str:
                return {
                    "success": False,
                    "error": "Quota de API insuficiente",
                    "response": "Seu limite de creditos na OpenAI foi atingido. Adicione creditos na sua conta OpenAI para continuar."
                }
            
            return {
                "success": False,
                "error": f"Erro na IA: {error_str[:100]}",
                "response": "Erro ao processar com a IA. Verifique a API key e tente novamente."
            }
        
    except Exception as e:
        error_str = str(e)
        print(f"[CHAT] [ERRO] ERRO GERAL: {error_str}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        return {
            "success": False,
            "error": error_str,
            "response": "Erro ao processar sua mensagem. Verifique os logs."
        }
