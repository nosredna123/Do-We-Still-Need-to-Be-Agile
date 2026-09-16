from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from Coletor import *
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from Estruturas import *
import json, os

load_dotenv()

app = Flask(__name__)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("API_KEY"))

llm_json = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("API_KEY"), response_mime_type="application/json")

def geracao_resumo_json_mode(user_prompt):
    template_resumo =   """
                        Your task is to produce a summary based on the content shared with you.
                        The summary MUST contain:

                            - keywords extracted from the content analyzed;
                            - the main topics covered, explained in rich detail;

                        Generate the summary in JSON format following this template: 

                            {{
                                "resumo": {{
                                    "titulo": "titulo do resumo",
                                    "conteudo": "todo o conteúdo do resumo"
                                }},
                                "lembretes": {{
                                    "lembrete1": {{
                                    "titulo": "titulo do lembrete",
                                    "descricao": "descricao do lembrete",
                                    "data": "data importante mencionada no material ou aula"
                                    }},
                                    "lembrete2": {{
                                    "titulo": "titulo do lembrete",
                                    "descricao": "descricao do lembrete",
                                    "data": "data importante mencionada no material ou aula (campo opcional)"
                                    }}
                                    .
                                    .
                                    .
                                }}
                            }}

                        NOTE:
                        Generate ONLY the JSON, and nothing else.
                        Do NOT generate ANY MARKDOWN, only a ***PLAIN STRING***.

                        Reminders consist of announcements made inside the content that mention dates.
                        If there is NO EXPLICIT date announcement, leave the DATE field EMPTY ("").

                        If a DAY, MONTH AND/OR YEAR is explicitly mentioned, return the date in ISO format:
                        YYYY-MM-DDTHH:mm:ss.sssZ.
                        If the time is not specified, FILL THE TIME WITH THE DEFAULT VALUE (00:00:00.000).
                        If the year is not explicit, use the current year (2025).

                        To categorize a reminder, search for messages that express upcoming future events such as:

                        Valid date examples:

                            - '[25/12] (valid date.): [there will be a holiday] (description), so there will be no class.'
                            - '[November 16 / 16/11] (valid date.) [I will attend a conference and will be away until the 26th] (description. The second date is optional.)'
                            - '[May 14, 2026 / 14/05] (valid date.), I will celebrate 50 years of marriage, therefore [there will be no class] (description)'

                        IMPORTANT:
                        If the content sent is in list format, schedule, calendar, table of events, class agenda, or sequence of dates,  
                        each line containing one or more dates must be interpreted as a separate reminder.

                        - If there are two dates in the same line (e.g., “11/11 e 13/11”), generate two identical reminders, varying only the date.  
                        - The title of the reminder must be the text immediately after the date (e.g., “Architecture Class”, “Project Delivery”, “Final Presentation”).  
                        - The description may be generated based on the general context of the material (e.g., “Delivery activity”, “Review class”, “Presentation of results”).  
                        - Whenever a line contains a date, generate a reminder, even if there is no verb or narrative context.  
                        - Interpret expressions such as “Calendar”, “Schedule”, “Agenda”, “Planning” as indications that the text is a list of events with dates.

                        In the reminders area, if there are no relevant reminders in the analyzed content, keep the reminders field empty, e.g., "lembretes": {{}}.
                        This reminder area is strictly for announcements made in class or within the material and is NOT directly related to the content of the summary.

                        The topic of this material is '{input}'.

                        THE OUTPUT ***MUST ALWAYS BE IN PORTUGUESE***, even though the instructions are written in English.
                        """
    
    parser_saida = PydanticOutputParser(pydantic_object=SaidaResumo)

    prompt = ChatPromptTemplate.from_template(template_resumo)

    chain = prompt | llm_json | parser_saida

    output = chain.invoke({
        "input": user_prompt
    })

    return output.model_dump()

def conversar_com_llm(mensagem:str, contexto, mensagensAnteriores):

    prompt_template = """
    Seu objetivo é responder a perguntas baseadas no contexto oferecido. Esse contexto é dividido da seguinte maneira:

    1) O CONTEXTO DO MATERIAL (principal fonte)
    2) AS MENSAGENS ANTERIORES (somente as que forem úteis)

    Use essas duas fontes para formular uma resposta precisa, objetiva e fiel ao conteúdo fornecido.

    MENSAGENS ANTERIORES (últimos turnos):
    {mensagens_anteriores}

    CONTEXTO DO MATERIAL ():
    {context}

    PERGUNTA:
    {input}

    INSTRUÇÕES IMPORTANTES:

    1) Priorize SEMPRE o conteúdo presente no CONTEXTO DO MATERIAL.  
    Se a resposta estiver ali, use-a diretamente.

    2) As MENSAGENS ANTERIORES servem apenas para manter continuidade da conversa  
    (ex: preferências, contexto da dúvida, histórico imediato).  
    Se alguma delas não tiver relevância para a pergunta atual, ignore.

    3) Caso o material não contenha informação suficiente para responder com exatidão:
    - NÃO invente informações.
    - Ao invés disso, ofereça:  
        a) os pontos do material mais próximos do tema solicitado,  
        b) possíveis direções para aprofundamento,  
        c) sugestões de tópicos correlatos presentes no contexto dado.

    4) Evite digressões. Seja direto, completo e claro.
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    response = chain.invoke({
        "mensagens_anteriores":mensagensAnteriores,
        "context": contexto,
        "input": mensagem
    })
    return response.content

def gerar_plano_de_estudo(user_prompt):
    template_plano_de_estudo =  """
                                Seu trabalho é trazer um plano de estudos, no estilo de um roadmap, para orientar um aluno em quais conteúdos priorizar, dado uma série de
                                materiais e assuntos.
                                O conteúdo esperado do plano de estudos consiste de:

                                - Uma lista simplificada do fluxo geral dos conteúdos, organizada em tópicos baseados em prioridade. Essa prioridade consiste em definir
                                o quão crucial aquele conteúdo é para que se possa compreender os assuntos seguintes. A lista deve conter todos os assuntos relevantes. Ex:
                                        1. Introdução a Ponteiros;
                                        2. Aritmética de Ponteiros;
                                        3. Ponteiros Aplicados em Estrutura de Dados;
                                        4. ...
                                    - Uma lista expandida, estruturada com a ordem dos tópicos, explicando o motivo para aquele conteúdo ter sido escolhido naquela ordem.
                                        OBS1: A explicação DEVE ser composta de 2 a 3 sentenças curtas.
                                        OBS2: NÃO mostre o contador de caracteres em nenhum ponto da conversa. É necessário apenas o conteúdo. 
                                        OBS3: A intenção desse limite é apenas para que sirva como uma breve justificativa e orientação para o que deve ser visto e por que.

                                    - Ao final da lista, baseado no que já foi explicado, gere uma segunda lista com conteúdos não explicitamente mencionados que podem ser
                                    relevantes para melhorar a compreensão do resumo. Ex:
                                        (mantendo o contexto de aula de ponteiros)
                                        a) Conceitos básicos de C;
                                        b) Estruturas de dados básicas (vetores e construtores);
                                        c) ...
                                        OBS: Os assuntos devem ser relevantes para o conteúdo e não puxar de conhecimentos que estão muito além do escopo estudado.
                                    REGRAS OBRIGATÓRIAS DE FORMATAÇÃO (SIGA SEMPRE):

                                    1. REGRAS PARA GERAÇÃO DOS SUMÁRIOS:
                                    - "title": uma sentença curta que sumarize o conteúdo passado. Evite usar termologia genérica, como 'Roteiro de Estudos (Tópicos Passados).'
                                    - "topicTitle": uma sentença curta que sumarize exatamente o que deve ser feito.
                                    - "description" (exceto checklist) deve ser composto de até 2 sentenças curtas e explicando a importância daquele tópico para o aprendizado.
                                    - "justification": de duas sentenças curtas, explicando o motivo da escolha daquele método para o tópico na primeira sentaça e abrindo um gancho 
                                    sobre a relação dessa com o próximo tópico com a segunda sentença.
                                    - checklist "description": composto de no máximo uma sentenças curtas, explicando o que o tópico da checklist espera.

                                    2. NÃO adicione explicações fora do JSON.

                                    3. REGRAS DOS TÓPICOS:
                                    - Evite enaltecer a importância do tópico de maneira expositiva dentro da justificativa. Ex. do que NÃO deve ser feito: "Este tópico é 
                                    fundamental para compreender o conceito de ponteiros e seus operadores básicos", "Este tópico demonstra a forte relação entre ponteiros 
                                    e arrays em C", "Compreender como ponteiros são usados na passagem de parâmetros para funções é essencial", etc.
                                    - A justificativa deve EXPLICITAR o 'porquê' de aquele tópico ser relevante, então opte por frases que denotem correlação. Ex: "Poteiros são essenciais para aprender
                                    como a linguagem C gerencia memória.", "Entender a relação entre Ponteiros e Arrays solidifica a base para compreensão de Estruturas de Dados mais complexas.", etc.

                                    3. REGRAS DA CHECKLIST:
                                    - Cada tópico deve ser composto de atividades concretas que permitam o enriquecimento do aprendizado do aluno.
                                    - EVITE pedir por atividades vagas ou sugestões educadas como "Estudar 'assunto X'", "Saber aplicar tais conhecimentos", isso são meios
                                    para que o aluno atinja os objetivos da checklist, e, portanto, não devem ser considerados como objetivos em si.
                                    - Novamente os checklists DEVEM ser relacionados com todo o conhecimento absorsvido dos materiais recebidos: 
                                        a) Se hoverem livros sobre o assunto como recomendações, recomende a leitura dos capítulos relacionados.
                                        b) Se for mencionado uma lista de exercícios, ou souber que dito material possui exercícios, priorize em recomendar os exercícios desse material
                                    - Exemplos do que se espera na geração da checklist:

                                        "checklist": 
                                            "item1": 
                                                "title": "Leitura Obrigatória",
                                                "orderIndex": 1,
                                                "description": "Ler Capítulo 3 do livro 'Introdução a Algoritmos (Cormen)'"

                                            "item2": 
                                                "title": "Fichamento",
                                                "orderIndex": 2,
                                                "description": "Definir 'Análise de Algoritmos' e 'Complexidade'"

                                            "item3": 
                                                "title": "Videoaula Introdutória",
                                                "orderIndex": 3,
                                                "description": "Assistir à videoaula 'Complexidade de Algoritmos - Conceitos Iniciais'"

                                            "item4": 
                                                "title": "Praticar",
                                                "orderIndex": 4,
                                                "description": "Identificar a notação O de 5 loops simples"


                                    Gere o plano de estudos seguindo o formato JSON especificado:

                                        {{
                                            "title": {{
                                                "title": "Titulo do plano de estudos"
                                            }},
                                            "topics": {{
                                                "topic1": {{
                                                    "title": "Nome do primeiro tópico prioritário",
                                                    "orderIndex": 1
                                                }},
                                                "topic2": {{
                                                    "title": "Nome do segundo tópico prioritário",
                                                    "orderIndex": 2
                                                }}
                                                ...
                                            }},
                                            "expandedTopics": {{
                                                "topic1": {{
                                                    "topicTitle": "Nome do primeiro tópico",
                                                    "orderIndex": 1,
                                                    "justification": "Explicação do porquê esse tópico vem nessa ordem"
                                                }},
                                                "topic2": {{
                                                    "topicTitle": "Nome do segundo tópico",
                                                    "orderIndex": 2,
                                                    "justification": "Explicação do porquê esse tópico vem nessa ordem"
                                                }}
                                                ...
                                            }},
                                            "complementaryTopics": {{
                                                "complemento1": {{
                                                    "title": "Conteúdo complementar relevante",
                                                    "description": "Descrição resumida da importância desse conteúdo adicional",
                                                    "orderIndex": 1
                                                }},
                                                "complemento2": {{
                                                    "title": "Outro conteúdo complementar",
                                                    "description": "Descrição resumida",
                                                    "orderIndex": 2
                                                }}
                                                ...
                                            }},
                                            "checklist": {{
                                                "item1": {{
                                                    "title": "Título do item da checklist",
                                                    "orderIndex": 1,
                                                    "description": "Descrição do que deve ser verificado / estudado"
                                                }},
                                                "item2": {{
                                                    "title": "Outro item da checklist",
                                                    "orderIndex": 2,
                                                    "description": "Descrição resumida do item"
                                                }}
                                                ...
                                            }}
                                        }}

                                    Os assuntos do plano de estudos são os seguintes {input}
                                    """
    
    parser_plano_de_estudos = PydanticOutputParser(pydantic_object=SaidaPlanoDeEstudos)

    prompt = ChatPromptTemplate.from_template(template_plano_de_estudo)

    chain = prompt | llm_json | parser_plano_de_estudos

    output = chain.invoke({
        "input": user_prompt
    })

    return output.model_dump()

@app.route("/generate", methods=["POST"])
def generate_summary():
    
    try:
        data = request.get_json()
        user_prompt = ""

        for transcript in data:
            user_prompt += transcript.get("content")
        if user_prompt == "":
            return jsonify({"error": "Campo 'material' é obrigatório"}), 400

        result = geracao_resumo_json_mode(user_prompt)
        try:
            json_result = result
        
        except json.JSONDecodeError:
            json_result = {"raw_output": result}
        
        return jsonify(json_result)

    except Exception as e:
        print(e)
        return jsonify({"error": e}), 500
    
@app.route("/studyplan", methods=["POST"])
def generate_study_plan():
    
    try:
        data = request.get_json()

        user_prompt = ""

        for topic_transcriptions in data:
            for transcript in topic_transcriptions:
                user_prompt += transcript.get("content")

        if user_prompt == "":
            return jsonify({"error": "Input vazio"}), 400

        result = gerar_plano_de_estudo(user_prompt)

        try:
            json_result = result
        
        except json.JSONDecodeError:
            json_result = {"raw_output": result}
        
        return jsonify(json_result)

    except Exception as e:
        print(e)
        return jsonify({"error": e}), 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        
        text = data['message']
        context = data['context']
        former_messages = data['formattedMessages']

        response = conversar_com_llm(text, context, former_messages)

        return jsonify({"resposta": response})
    except Exception as e:
        print(e)
        return jsonify({"error": e}), 500

@app.route("/transcript", methods=["POST"])
def transcript_test():
    
    data = request.json
    results = []

    for obj in data:
        path = obj.get("public_url")
        material_id = obj.get("id")
        filename = path.split("/")[-1]

        if not path:
            return jsonify({"error": "File path unknown"}), 400
        
        try:
            transcricao = pdf2md_extractor(path)
            results.append({
                "material_id": material_id,
                "filename": filename,
                "transcription": transcricao
            })
        except Exception as e:
            results.append({
                "material_id": material_id,
                "filename": filename,
                "transcription": "" 
            })
            continue


    return jsonify({"results": results}), 200

@app.route("/embed", methods=["POST"])
def embed_chunk():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Campo 'text' é obrigatório"}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "O texto do chunk está vazio"}), 400

    try:
        embedding = gerar_embeddings(text)
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar embedding: {str(e)}"}), 500

    return jsonify({"results": embedding}), 200
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

