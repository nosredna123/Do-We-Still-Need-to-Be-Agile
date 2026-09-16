   IDEIAS:

Interview Prep IA - Sistema com IA que analisa currículo, compara com uma vaga, simula entrevista e gera feedback personalizado para ajudar candidatos a se prepararem melhor para processos seletivos.

     Duas entradas->Currículo e Vaga.
     Respostas por meio de texto,gerar possíveis questões que podem aparecer na  entrevista.
     Baseado nas respostas, montar um treinamento.
     Linguagem Python com FastApi, integração com IA propria.

     Interface Front-End com React
    Banco de dados não relacional - MongoDB



Fluxograma:
	
entrada: currículo + descrição da vaga
processamento: análise de aderência + geração de perguntas de entrevista
saída: feedback personalizado + plano de treino

# Conceito central

O usuário informa:

* seu currículo;
* a vaga desejada;
* talvez nível de experiência.

O sistema faz:

1. analisa o currículo em relação à vaga;
2. identifica pontos fortes e lacunas;
3. gera perguntas prováveis de entrevista;
4. permite que o usuário responda;
5. devolve feedback personalizado;
6. monta um plano de treino.

---

# Isso é um bom projeto?

Sim, porque resolve um problema concreto:

* muita gente não sabe adaptar currículo;
* muita gente não sabe se preparar para entrevista;
* o sistema gera valor claro e demonstrável.



### 1. Análise de currículo vs vaga

O usuário cola:

* currículo
* descrição da vaga

O sistema retorna:

* compatibilidade geral
* palavras-chave encontradas
* palavras-chave faltantes
* sugestões de melhoria

### 2. Geração de perguntas de entrevista

Com base na vaga, o sistema gera:

* perguntas técnicas
* perguntas comportamentais
* perguntas sobre experiência
* perguntas sobre fit com a vaga

### 3. Respostas do candidato

O usuário responde em texto.

### 4. Feedback e plano de treino

O sistema avalia:

* clareza
* objetividade
* aderência à vaga
* pontos a melhorar

E monta:

* tópicos para estudar
* perguntas para praticar de novo
* competências a reforçar

Isso já fecha um projeto muito bom.
# Arquitetura simples

## Frontend

* React
* MUI

## Backend

 FastAPI

## IA

* API pronta para análise e geração de texto

## Banco

* MongoDB, SQlite, Firebase ou até JSON/local no MVP

---

# Fluxo do usuário

1. Usuário acessa a página.
2. Cola currículo.
3. Cola descrição da vaga.
4. Clica em “Analisar”.
5. Vê aderência e sugestões.
6. Clicar em “Simular entrevista”.
7. O sistema gera de 5 a 10 perguntas.
8. O usuário responde.
9. Sistema devolve feedback.
10. Sistema gera plano de treino.

obs: os itens 6, 7, e 8. pode-se fazer uma melhoria. Uma sugestão mais ativa e melhor seria uma conversa entre usuário e bot, para simular uma entrevista de emprego, isso seria um ponto relevante para próximas versões.

Seguindo a Sugestão na apresentação, de no caso fazer um radar para ver outras vagas que no caso o currículo do usuário seria mais compatível 


# Melhor forma de vender a ideia

Apresentem como uma plataforma de apoio à empregabilidade.

## Problema

Muitos candidatos têm dificuldade em:

* adaptar o currículo à vaga;
* identificar lacunas;
* praticar entrevistas;
* receber feedback estruturado.

## Solução

Uma aplicação com IA que:

* analisa currículo e vaga;
* simula entrevista;
* gera feedback personalizado;
* orienta o treino do candidato.

## Impacto

* melhora a preparação do usuário;
* aumenta confiança;
* organiza o processo de candidatura.

---

# Divisão realista para 2 pessoas ativas

## Pessoa 1

Frontend:

* telas
* fluxo do usuário
* formulários
* exibição dos resultados

## Pessoa 2

Backend/IA:

* integração com modelo
* regras de análise
* geração dos feedbacks
* estrutura dos prompts

## Restante do grupo

* documentação
* slides
* testes
* relatório
* benchmark/manual do usuário

---

# Escopo ideal em 3 meses

## Mês 1

* definir requisitos
* escolher stack
* montar telas principais
* integrar primeira chamada de IA
* fazer análise básica currículo x vaga

## Mês 2

* implementar geração de perguntas
* implementar envio de respostas
* gerar feedback textual
* refinar UX

## Mês 3

* plano de treino
* ajustes finais
* testes
* documentação
* apresentação

## Cronograma
  ![Cronograma](/img/cronograma.png)

---
## Tema final

*Plataforma de preparação para processos seletivos com IA*

## Funcionalidades principais

* análise de currículo com base na vaga;
* geração de perguntas de entrevista;
* feedback textual personalizado;
* plano de treino do candidato.

## Documentação de reuniões
  * Docs   : https://docs.google.com/document/d/1CleqVNDyl2turzioFoQyi_yfZZ1-Kv3JtuXD9W8mojM/edit?usp=sharing
  * Trello : https://trello.com/invite/b/69f63fcf6520d5d9587b4ea3/ATTIc5e469a8cf53b2668568bddc40735799C93A7AD2/extensao-3
  * Sheets : https://docs.google.com/spreadsheets/d/1qG1PVusJjrarHl880kbnHyd6oDPCnAdaz7nyBqV7Qng/edit?usp=sharing


# Como Executar a Aplicação (Back-end)

## Pré-requisitos

Antes de iniciar o projeto, certifique-se de ter instalado:

* Python 3.10 ou superior
* Pip (gerenciador de pacotes do Python)

## 1. Clonar o Projeto

```bash
git clone <url-do-repositorio>
cd <nome-do-projeto>
cd BACKEND
```

## 2. Criar e Ativar um Ambiente Virtual

### Windows

```bash
python -m venv venv
venv/Scripts/activate
```

### Linux/Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalar as Dependências

Instale todas as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

## 4. Configurar as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto e adicione:

```env
GROQ_API_KEY=sua_chave_groq
```

### Obtendo a chave da Groq

1. Acesse o console da Groq:
   https://console.groq.com

2. Crie uma conta gratuita.

3. Gere uma API Key.

4. Copie a chave gerada para a variável `GROQ_API_KEY` no arquivo `.env`.

## 5. Executar a Aplicação

Inicie o servidor FastAPI com o Uvicorn:

```bash
python -m uvicorn main:app --port 8000
```

A API ficará disponível em:

```text
http://localhost:8000
```

## 6. Acessar a Documentação da API

### Swagger UI

```text
http://localhost:8000/docs
```

### ReDoc

```text
http://localhost:8000/redoc
```

# Como Executar a Aplicação (Front-end)

Interface web do projeto **Interview Prep IA**, desenvolvida com **React + TypeScript + Vite**.

O front-end é responsável por:

* receber o currículo do usuário;
* receber o texto da vaga;
* enviar os dados para a API;
* exibir o resultado da análise de compatibilidade;
* apresentar pontos fortes, pontos fracos e habilidades faltantes;
* permitir cenários adicionais, como:

  * simulação de perguntas de entrevista;
  * sugestões de melhoria;
* exibir os retornos da IA de forma visual e organizada.

---

## Tecnologias utilizadas

* React
* TypeScript
* Vite
* Material UI (MUI)
* Axios

---

## Pré-requisitos

Antes de iniciar o front-end, certifique-se de ter instalado:

* Node.js 18 ou superior
* npm 9 ou superior

---

## 1. Acessar a pasta do front-end

```bash
cd frontend
```

---

## 2. Instalar as dependências

```bash
npm install
```

---

## 3. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz da pasta do front-end com o conteúdo:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Essa variável define o endereço base da API utilizada pelo front-end.

---

## 4. Executar o front-end em ambiente de desenvolvimento

```bash
npm run dev
```

A aplicação ficará disponível em:

```text
http://localhost:5173
```

---

## Observação

Para o funcionamento completo da aplicação, o back-end deve estar em execução antes de utilizar o front-end.

O back-end deve estar disponível em:

```text
http://localhost:8000
```
