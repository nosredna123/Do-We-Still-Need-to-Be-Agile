import os 
import time
import base64
import requests
import openai
import google.generativeai as genai
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

# Configurações das credenciais
host = os.getenv("HOST_API")
api_key = os.getenv("API_KEY")

def processar_imagem(instance:str, message_id:str, ia_infos) -> str:
    print("Processando imagem...")
    imagem_transcript = "Imagem enviada: Não consegui transcrever essa imagem. Fale para o usuário que a internet está instável e que não foi possível baixar a imagem."

    try:
        url = host+"chat/getBase64FromMediaMessage/"+instance

        body = {
            "message": {"key": {"id": message_id}},
            "convertToMp4": False
        }

        data = post_request(url, body)
        
        if data.get("status_code") in [200, 201]:
            image_base64 = data.get("response")["base64"]
            
            # Pega a chave da API e o modelo configurado para essa IA
            api_key_ia = ia_infos.ia_config.credentials.get("api_key")
            model_name = os.getenv("MODEL_ANALYZE_IMAGE", "gpt-4o").lower()

            # ==========================================
            # MOTOR DO GOOGLE GEMINI
            # ==========================================
            if "gemini" in model_name:
                print(f"Visão acionada via Gemini: {model_name}")
                genai.configure(api_key=api_key_ia)
                model = genai.GenerativeModel(model_name)
                
                image_parts = [{"mime_type": "image/jpeg", "data": image_base64}]
                
                response = model.generate_content([
                    "Faça uma interpretação detalhada da imagem enviada.", 
                    image_parts[0]
                ])
                imagem_transcript = response.text

            # ==========================================
            # MOTOR DA OPENAI
            # ==========================================
            else:
                print(f"Visão acionada via OpenAI: {model_name}")
                header = {
                    "Authorization": f"Bearer {api_key_ia}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Faça uma interpretação detalhada da imagem enviada."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                            ]
                        }
                    ],
                    "max_tokens": 500
                }

                url_openai = "https://api.openai.com/v1/chat/completions"
                response = requests.post(url_openai, headers=header, json=payload, timeout=30)
                
                if response.status_code == 200:
                    response_json = response.json()
                    imagem_transcript = response_json["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"Erro na API da OpenAI: {response.text}")

            print(f"Imagem transcrita com sucesso!")

    except Exception as ex:
        print(f"Erro ao transcrever imagem: {ex}")

    return imagem_transcript


def processar_audio(instance:str, message_id:str, ia_infos) -> str:
    print("Processando áudio...")
    audio_transcript = "Áudio enviado: Não consegui transcrever esse áudio. Peça para o usuário enviar a mensagem em texto."
    timestamp = str(time.time())
    
    audio_path = f"audio_{timestamp}.ogg"
    mp3_path = f"audio_{timestamp}.mp3"
    
    try:
        url = host+"chat/getBase64FromMediaMessage/"+instance
        body = {
                "message": {"key": {"id": message_id}},
                "convertToMp4": False
            }
        data = post_request(url, body)

        if data.get("status_code") in [200, 201]:
            audio_base64 = data.get("response")["base64"]
            audio_bytes = base64.b64decode(audio_base64)
            
            # Salva o OGG original
            with open(audio_path, "wb") as audio_file:
                audio_file.write(audio_bytes)
            
            # Converte para MP3
            audio = AudioSegment.from_ogg(audio_path)
            audio.export(mp3_path, format="mp3")

            api_key_ia = ia_infos.ia_config.credentials.get("api_key")
            model_name = os.getenv("MODEL_TRANSCRIBE_AUDIO", "whisper-1").lower()

            # ==========================================
            # MOTOR DO GOOGLE GEMINI
            # ==========================================
            if "gemini" in model_name:
                print(f"Transcrição acionada via Gemini: {model_name}")
                genai.configure(api_key=api_key_ia)
                
                # Sobe o MP3 para o Google
                arquivo_gemini = genai.upload_file(mp3_path)
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content([
                    "Transcreva exatamente o que está sendo dito neste áudio. Retorne apenas o texto falado.",
                    arquivo_gemini
                ])
                audio_transcript = f"Áudio enviado: {response.text}"
                
                # Limpa o arquivo na nuvem do Google após transcrever
                genai.delete_file(arquivo_gemini.name)

            # ==========================================
            # MOTOR DA OPENAI
            # ==========================================
            else:
                print(f"Transcrição acionada via OpenAI: {model_name}")
                openai.api_key = api_key_ia

                with open(mp3_path, "rb") as audio_file:
                    response = openai.audio.transcriptions.create(
                        model=model_name,
                        file=audio_file
                    )
                audio_transcript = f"Áudio enviado: {response.text}"

        else:
            raise Exception(f"Erro ao coletar dados da api: {data}")
        
    except Exception as ex:
        print(f"Erro ao transcrever áudio: {ex}")

    # Limpeza dos arquivos locais
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
    except Exception as e:
        print(f"Erro ao deletar arquivos temporários: {e}")

    return audio_transcript

def send_message(instance:str, lead_phone:str, message:str, delay:int) -> dict:
    url = host+"message/sendText/"+instance
    body = {
        "number": lead_phone,
        "options": {
            "delay": int(delay)*1000,
            "presence": "composing",
            "linkPreview": False
        },
        "textMessage": {
            "text": str(message)
        }
    }

    data = post_request(url, body)
    return data

def post_request(url:str, body:dict, max_retries:int=5, wait_seconds:int=5) -> dict:
    attemp = 0
    lead = body.get("number", "undefined")
    response_post = {"status_code": None, "response":None}

    headers = {
        "apikey":api_key,
        "Content-Type":"application/json"
    }

    while attemp < max_retries:
        attemp +=1
        response = requests.post(url, json=body, headers=headers, timeout=120)

        try:
            response_return = response.json()
        except Exception as ex:
            response_return = response.text

        if response.status_code in [200, 201]:
            response_post = {"status_code": response.status_code, "response":response_return}
            return response_post
        
        if attemp < max_retries:
            time.sleep(wait_seconds)

    return response_post