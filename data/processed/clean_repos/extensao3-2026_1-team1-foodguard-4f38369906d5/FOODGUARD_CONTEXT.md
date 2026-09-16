# FoodGuard - Documento de Contexto do Sistema

**Versão:** 1.0  
**Data:** Abril 2026  
**Instituição:** Universidade Estadual do Ceará - Curso de Ciência da Computação  
**Disciplina:** Extensão III

---

## 1. Visão Geral

**FoodGuard** é uma plataforma web para identificação de componentes alergênicos em produtos alimentícios, prevenindo reações adversas em usuários. O sistema realiza análise inteligente de rótulos através de código de barras ou texto, cruzando dados nutricionais com histórico médico (anamnese) do usuário.

### Objetivo Principal
Fornecer uma solução ágil e intuitiva para verificação de segurança alimentar baseada em:
- Leitura de códigos de barras (Yolov8n + ONNX Runtime-web)
- Processamento de linguagem natural (LLM - Gemini)
- Histórico de saúde personalizado (anamnese)

---

## 2. Fluxo de Usuário

### Onboarding (Primeira Vez)
1. **Cadastro de Perfil** [RF001]
   - Coleta: nome completo, email, data de nascimento, senha
   - Validações: email único, senha com ≥8 caracteres (maiúscula + minúscula + número)
   - Feedback: sucesso → avanço automático para anamnese

2. **Cadastro de Anamnese** [RF002]
   - Formulário obrigatório com histórico de saúde
   - Acesso ao chat bloqueado até preenchimento completo
   - Conclusão: acesso total à plataforma

### Uso Contínuo
1. **Autenticação** [RF003]
   - Login via Firebase Authentication
   - Sessão expira após 24h de inatividade

2. **Interação com Chat** [RF008, RF009]
   - Modo texto: envio de dúvidas sobre alimentos
   - Modo imagem: upload de código de barras (PNG/JPEG/JPG, máx 10MB)
   - Processamento com contexto de anamnese do usuário
   - Resposta personalizada baseada em restrições dietéticas/alergias

3. **Gestão de Histórico** [RF011, RF012, RF013]
   - Sidebar com chats anteriores
   - Edição de último prompt
   - Exclusão de conversas com confirmação

4. **Perfil e Configurações** [RF014, RF015, RF016, RF017]
   - Visualização/edição de dados pessoais (name, email, DOB)
   - Visualização/edição de anamnese
   - Logout com confirmação

---

## 3. Requisitos Funcionais Principais

| ID | Funcionalidade | Status | Notas |
|---|---|---|---|
| RF001 | Cadastro de Perfil | Ativo | Validações obrigatórias |
| RF002 | Cadastro de Anamnese | Ativo | Bloqueia acesso ao chat |
| RF003 | Login | Ativo | Firebase Authentication |
| RF004 | Recuperação de Senha | Ativo | Email com link Firebase |
| RF005 | Home/Navegação | Ativo | Scroll suave para seções |
| RF006 | Acesso ao Chat | Ativo | Requer autenticação |
| RF007 | Nova Conversa | Ativo | Sidebar dinâmica |
| RF008 | Chat via Texto | Ativo | Máx 5.000 caracteres |
| RF009 | Chat via Imagem | Ativo | Extração de código de barras |
| RF010 | Perguntas Frequentes | **Depreciado** | Em vermelho no doc |
| RF011 | Histórico de Conversas | Ativo | Persistência em banco |
| RF012 | Edição de Prompt | Ativo | Regenera última resposta |
| RF013 | Exclusão de Chats | Ativo | Modal de confirmação |
| RF014 | Menu de Perfil | Ativo | Dropdown na navbar |
| RF015 | Edição de Perfil | Ativo | Inputs bloqueados por padrão |
| RF016 | Edição de Anamnese | Ativo | Bloqueia chats antigos |
| RF017 | Logout | Ativo | Invalida token JWT/Firebase |

---

## 4. Requisitos de Qualidade

### RQ001: Usabilidade e Acessibilidade
- Feedbacks visuais em ≤500ms
- Smooth scroll ≤800ms (Home → seções)

### RQ002: Segurança, Privacidade e Conformidade (LGPD)
- Senhas: hash irreversível via Firebase (scrypt/bcrypt)
- **Dados de saúde:** mascarar identificadores (nome, email, DOB) antes de enviar ao LLM
- Anamnese: exclusivo para composição de prompt + visualização do usuário
- **Proibido:** compartilhar dados médicos com terceiros ou APIs de publicidade
- Sessão: expiração automática após 24h inatividade

### RQ003: Desempenho
- Indicador visual de loading obrigatório
- Resposta de LLM (texto): ≤15 segundos
- Extração de código de barras (Yolov8n): ≤8 segundos (fallback se exceder)

### RQ004: Persistência e Consistência
- Salvar mensagens/contexto em tempo real
- Exclusão de chats refletida imediatamente (UI + banco)

---

## 5. Regras de Negócio Críticas

### RN001: Obrigatoriedade da Anamnese
- Acesso ao Chat bloqueado sem anamnese completa
- Novo login → força preenchimento antes do chat
- Dependência: todos os prompts usam contexto de anamnese

### RN002: Validação de Entrada de Imagem
- Apenas PNG, JPEG, JPG
- Máximo 10MB
- Rejeita outros formatos silenciosamente

### RN003: Limite de Texto
- Prompts de texto: máx 5.000 caracteres
- Garante desempenho de NLP

### RN004: Integridade do Histórico de Saúde
- Alteração de anamnese → bloqueia chats anteriores
- Força nova conversa com contexto atualizado
- Aviso visual: "conversa usando dados desatualizados"

### RN005: Criptografia de Credenciais
- **Zero senhas em texto plano**
- Delegado 100% ao Firebase Authentication

### RN006: Privacidade de Dados de Saúde
- Dados de anamnese: **uso exclusivo para prompt do LLM + visualização do usuário**
- **Estritamente proibido:** compartilhar com terceiros ou APIs de publicidade

### RN007: Restrição de Acesso por Sessão
- Rotas protegidas requerem autenticação
- Acesso direto via URL sem token → redirecionamento para Home/Login

### RN008: Feedback de Processamento (Debounce)
- Inputs desabilitados durante processamento do LLM
- Estado de loading visível
- Previne múltiplos envios acidentais

### RN009: Persistência de Contexto
- Ao retomar chat: reconstruir e enviar histórico completo ao LLM
- Mantém continuidade lógica da conversa

### RN010: Edição de Perfil Restrita
- Nome, email, DOB: visualização apenas
- Usuário/Senha: editáveis
- Email: validação de unicidade obrigatória

### RN011-RN014: Validações de Campo

| Campo | Requisito | Detalhe |
|---|---|---|
| **Email** | Padrão + único | `parteLocal@domínio.com`, não pode duplicar |
| **Senha** | ≥8 char | Maiúscula + minúscula + número |
| **Nome** | Máx 250 char | Aceita: alfabeto, acentos, espaços, apóstrofos, hífens. Rejeita: números e símbolos |
| **Carregamento ChatBot** | Bloqueio total | Botão envio + campo digitação bloqueados até resposta renderizada |

---

## 6. Stack Técnico Mencionado

### Frontend
- **Barcode Detection:** zbar-wasm (leitura de código de barras)
- **Yolov8n + ONNX Runtime-web** (modelo de visão computacional para extração do código)

### Backend
- **Autenticação:** Firebase Authentication
- **Banco de Dados:** Firebase (conversas, usuários)
- **LLM:** Google Gemini API (processamento de prompts)
- **API de Alimentos:** integração externa (resgate de ingredientes)

### Segurança
- **Hash de Senha:** scrypt/bcrypt (nativo Firebase)
- **Sessão:** JWT/Firebase token com expiração 24h

---

## 7. Estrutura de Dados Esperada

### Usuário
```
{
  id: string (Firebase UID),
  email: string (único),
  nome: string (≤250 char),
  dataNascimento: date,
  criadoEm: timestamp,
  ultimoAcesso: timestamp
}
```

### Anamnese
```
{
  userId: string,
  perguntas: {
    [pergunta]: resposta
  },
  completa: boolean,
  atualizadoEm: timestamp
}
```

### Chat/Conversa
```
{
  id: string,
  userId: string,
  anamneseVersionId: string (para rastrear bloqueio),
  mensagens: [
    {
      role: "user" | "assistant",
      tipo: "texto" | "imagem",
      conteudo: string,
      timestamp: timestamp,
      metadados?: { codigoBarras?, ingredientes? }
    }
  ],
  criadoEm: timestamp,
  atualizadoEm: timestamp
}
```

---

## 8. Estados Críticos de UI

### Estados de Input
- **Default:** habilitado
- **Loading/Processando:** desabilitado + spinner visível
- **Erro:** campo destacado em vermelho + mensagem específica
- **Bloqueado:** desabilitado + indicador visual (strikethrough, opacity, ícone de cadeado)

### Estados de Modal
- **Confirmação:** antes de logout, exclusão de chat, edição de anamnese
- **Feedback:** toast com sucesso/erro/info (visual + mensagem)

### Estados de Conversa
- **Nova:** conversação em branco
- **Ativa:** aceita prompts normalmente
- **Bloqueada (anamnese desatualizada):** 
  - Aceita leitura de histórico
  - Rejeita novos prompts
  - Exibe aviso: "Dados desatualizados - crie nova conversa"

---

## 9. Fluxos Críticos de Erro

### RF009 (Chat via Imagem)
1. **Código ilegível** → mensagem amigável sugerindo foto nítida ou texto
2. **Arquivo inválido** (formato/tamanho) → rejeição + orientação
3. **Timeout barcode (>8s)** → aborta processamento + fallback com erro
4. **API de alimentos fora do ar** → graceful degradation

### RF003 (Login)
1. **Usuário não encontrado** → mensagem genérica (privacidade)
2. **Senha incorreta** → mensagem genérica
3. **Muitas tentativas** → rate limiting (Firebase nativo)
4. **Anamnese incompleta** → redireciona para formulário antes do chat

---

## 10. Prioridades de Implementação

### P0 (Bloqueador)
- Autenticação (RF003)
- Cadastro + Anamnese (RF001, RF002)
- Chat básico texto (RF008)
- Privacidade de dados (RN006)

### P1 (Essencial)
- Chat por imagem (RF009)
- Histórico de conversas (RF011)
- Logout (RF017)
- Validações de campo (RN011-RN014)

### P2 (Feature)
- Edição de prompt (RF012)
- Edição de anamnese (RF016)
- Home com navegação (RF005)

### P3 (Nice-to-have)
- Perguntas frequentes (RF010 - **Depreciado**)

---

## 11. Histórico de Desenvolvimento

| Data | Etapa |
|---|---|
| 23/03/2026 | Criação dos Requisitos Funcionais (RF) |
| 24/03/2026 | Descrição geral do sistema |
| 31/03/2026 | Criação dos Requisitos de Qualidade (RQ) |
| 02/04/2026 | Criação das Regras de Negócio (RN) |

---

## Notas para Desenvolvimento

- **LGPD Compliance:** crítico - dados de saúde são sensíveis
- **Gemini Integration:** verificar temperatura e prompts de sistema
- **Yolov8n Performance:** testar em diferentes dispositivos/câmeras
- **Firebase Quotas:** considerar custos de autenticação e firestore
- **Barcode Formats:** validar suporte (EAN-13, UPC, Code128)
- **Fallback UI:** implementar graceful degradation quando barcode falhar
