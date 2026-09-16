# ✅ Checklist - Configurar Chat para Funcionar

## 1️⃣ **Verificar IA Cadastrada**

Acesse: http://127.0.0.1:5000

- [ ] Há alguma IA listada?
- [ ] Se NÃO, crie uma IA clicando em "Criar IA"

**Dados sugeridos:**
```
Nome: Julie
Telefone: 5585999999999
Canal: whatsapp
IA: openai (ou gemini)
API Key: sua-chave-aqui
Modelo: gpt-4o-mini
```

---

## 2️⃣ **Configurar Prompt para a IA**

- [ ] Clique em "Prompts"
- [ ] Clique em "+ New Prompt"
- [ ] Selecione a IA criada
- [ ] Cole um prompt:

```
Você é Julie, uma assistente de IA amigável e útil.
Responda perguntas com clareza e educação.
Se não souber algo, diga honestamente.
```

- [ ] Marque "Status" como ✓ (ativo)
- [ ] Clique em "Save"

---

## 3️⃣ **Verificar API Keys no .env**

Abra `.env` e preencha:

```env
OPENAI_API_KEY=sua-chave-openai-aqui
# OU
GEMINI_API_KEY=sua-chave-gemini-aqui
```

---

## 4️⃣ **Rodar os Servidores**

**Terminal 1 (FastAPI):**
```bash
cd "d:\Downloads HD\SmartFlow-WhatsApp-AI-dev-2\SmartFlow-WhatsApp-AI-dev-2"
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Flask):**
```bash
cd "d:\Downloads HD\SmartFlow-WhatsApp-AI-dev-2\SmartFlow-WhatsApp-AI-dev-2"
python interface\app\app.py
```

---

## 5️⃣ **Testar o Chat**

- [ ] Acesse: http://127.0.0.1:5000/chat
- [ ] Digite uma mensagem
- [ ] Verifique os logs do FastAPI (Terminal 1)

---

## 🐛 **Troubleshooting**

### ❌ "IA não encontrada"
- [ ] Crie uma IA em http://127.0.0.1:5000
- [ ] Ativa a IA (Status = ON)

### ❌ "Nenhum prompt ativo"
- [ ] Vá em Prompts
- [ ] Crie um prompt para a IA
- [ ] Marque como "Ativo" (✓)

### ❌ "Nenhuma API key"
- [ ] Preencha OPENAI_API_KEY ou GEMINI_API_KEY no .env
- [ ] Reinicie o FastAPI

### ❌ "Erro na IA: ..."
- [ ] Verifique os logs do FastAPI (Terminal 1)
- [ ] Procure por `[CHAT]` para ver o fluxo

---

## 📝 **Logs do FastAPI**

Procure por linhas assim:

```
[CHAT] Recebido: message=que horas abre a uece?... ia_id=1
[CHAT] Buscando IA com ID 1...
[CHAT] ✓ IA encontrada: Julie
[CHAT] ✓ Prompt ativo encontrado
[CHAT] ✓ API key configurada. Model: gpt-4o-mini
[CHAT] Gerando resposta com LLM...
[CHAT] ✓ Resposta gerada com sucesso: ...
```

Se ver um **❌**, é o erro.

---

## 💡 **Dica**

Se ainda não tiver IA cadastrada, você pode criar pelo painel:
1. Acesse http://127.0.0.1:5000
2. Clique em "Create IA"
3. Preencha os dados
4. Clique em "Save"

Depois crie um prompt e ative-o.

---

**Status:** ✅ Pronto para usar!
