# Casos de Uso — Sistema SoFiA

## UC-01 — Registrar despesa via chat
**Atores:** Usuário  
**Pré-condições:** Usuário autenticado e sessão de chat ativa  
**Fluxo principal:**
1. O usuário envia uma mensagem como "gastei 50 reais em Uber hoje".
2. O sistema (LLM) identifica a intenção de registrar uma despesa e extrai os dados (valor, descrição, data).
3. O sistema sugere uma categoria (ex.: Transporte) e solicita confirmação.
4. O usuário confirma.
5. O sistema salva a transação.
**Pós-condições:** A despesa é registrada e aparece no histórico e no dashboard.

---

## UC-02 — Registrar ganho via chat
**Atores:** Usuário  
**Pré-condições:** Usuário autenticado e sessão de chat ativa  
**Fluxo principal:**
1. O usuário envia mensagem como "recebi 2500 de salário".
2. O sistema identifica que é um ganho/receita.
3. O sistema extrai os dados e sugere categoria.
4. O usuário confirma.
5. O sistema registra o ganho.
**Pós-condições:** A receita aparece no histórico e atualiza o saldo.

---

## UC-03 — Editar categoria ou transação
**Atores:** Usuário  
**Pré-condições:** Transação existente  
**Fluxo principal:**
1. O usuário acessa a lista de transações.
2. Seleciona uma transação para editar.
3. Altera categoria, valor, descrição ou data.
4. Salva as alterações.
**Pós-condições:** A transação é atualizada e o dashboard reflete a alteração.

---

## UC-04 — Importar extrato financeiro (upload)
**Atores:** Usuário  
**Pré-condições:** Arquivo disponível (CSV, OFX, etc.)  
**Fluxo principal:**
1. O usuário acessa a tela de importação.
2. Faz upload do extrato.
3. O sistema processa o arquivo e exibe uma prévia das transações.
4. O usuário confirma (ou ajusta categorias).
5. O sistema salva todas as transações.
**Pós-condições:** Transações importadas aparecem no histórico e dashboard.

---

## UC-05 — Visualizar dashboard financeiro
**Atores:** Usuário  
**Pré-condições:** Existência de transações no sistema  
**Fluxo principal:**
1. O usuário acessa o dashboard.
2. O sistema exibe gráficos, saldo, comparações mensais e histórico.
3. O usuário pode aplicar filtros (categoria, período, valor).
**Pós-condições:** O usuário visualiza informações financeiras organizadas e atualizadas.

---

## UC-06 — Perguntar ao LLM sobre finanças
**Atores:** Usuário  
**Pré-condições:** Existência de dados relevantes  
**Fluxo principal:**
1. O usuário pergunta algo como "Quanto gastei em transporte este mês?".
2. O sistema interpreta a pergunta via LLM.
3. O sistema consulta o banco e calcula a resposta.
4. Exibe a resposta ao usuário.
**Pós-condições:** O usuário obtém insights financeiros em linguagem natural.

---

## UC-07 — Filtrar e buscar transações
**Atores:** Usuário  
**Pré-condições:** Histórico populado  
**Fluxo principal:**
1. O usuário acessa a tela de histórico.
2. Aplica filtros por categoria, período, tipo ou valor.
3. O sistema exibe somente as transações filtradas.
**Pós-condições:** O usuário visualiza apenas os dados desejados.

