const BASE_URL = "http://127.0.0.1:8000";

// URL para os endpoints da API (v1) - Para chat, rag, calendar
const API_URL = `${BASE_URL}/v1`;

export const api = {

  // ============================================================
  // AUTENTICAÇÃO
  // ============================================================

  // 1. LOGIN GOOGLE: Redireciona o usuário para o endpoint de OAuth
  // Isso tira o usuário da aplicação React e o leva para o fluxo do Google.
  // IMPORTANTE: O seu Back-end deve estar configurado para redirecionar
  // de volta para o Front-end (/chat) após o login ser concluído com sucesso.
  loginGoogle: () => {
    window.location.href = `${BASE_URL}/auth/login`;
  },

  logout: async () => {
    const response = await fetch(`${BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Adicione o token aqui se sua API exigir autenticação via Header
        // 'Authorization': `Bearer ${sessionStorage.getItem('token')}`
      },
    });

    if (!response.ok) {
      throw new Error(`Erro ao realizar logout: ${response.statusText}`);
    }

    return true; // Retorna true indicando que o back-end processou a saída
  },

  // ============================================================
  // CHATBOT & INTENÇÃO
  // ============================================================

  // 2. O CÉREBRO: Classifica o que o usuário quer dizer
  classifyIntent: async (text) => {
    try {
      const response = await fetch(`${API_URL}/chat/classify_intent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text }),
      });

      if (!response.ok) {
        throw new Error(`Erro API: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Erro ao classificar intenção:", error);
      return null;
    }
  },

  // 3. O RAG: Consulta a bula do medicamento
  queryRag: async (originalQuery, topic) => {
    try {
      const response = await fetch(`${API_URL}/rag/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            original_query: originalQuery,
            topic: topic
        }),
      });

      if (!response.ok) {
        throw new Error(`Erro API RAG: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Erro no RAG:", error);
      return { response: JSON.stringify({ answer: "Desculpe, não consegui conectar ao servidor." }) };
    }
  },

  // ============================================================
  // CALENDÁRIO
  // ============================================================

  // 4. CALENDAR: Agendar um tratamento
  scheduleTreatment: async (instrucao, startTime = "agora") => {
    try {
      const response = await fetch(`${API_URL}/calendar/schedule`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            instrucao: instrucao,
            start_time_str: startTime
        }),
      });
      return await response.json();
    } catch (error) {
      console.error("Erro ao agendar:", error);
      return { message: "Erro ao agendar." };
    }
  },

  // 5. CALENDAR: Listar eventos de um medicamento
  getEvents: async (medicamento) => {
    try {
      const response = await fetch(`${API_URL}/calendar/events/${medicamento}`);
      return await response.json();
    } catch (error) {
      console.error("Erro ao buscar eventos:", error);
      return { events: [] };
    }
  },

  // 6. CALENDAR: Deletar eventos
  deleteEvents: async (eventIds) => {
    try {
      const response = await fetch(`${API_URL}/calendar/delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event_ids: eventIds }),
      });
      return await response.json();
    } catch (error) {
      console.error("Erro ao deletar:", error);
      return { message: "Erro ao deletar." };
    }
  },

  // 7. CALENDAR: Editar um evento
  editEvent: async (eventId, newStartTime) => {
    try {
      const response = await fetch(`${API_URL}/calendar/edit/${eventId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_start_time_str: newStartTime }),
      });

      if (!response.ok) {
         const err = await response.json();
         throw new Error(err.detail || "Erro ao editar");
      }
      return await response.json();
    } catch (error) {
      console.error("Erro ao editar:", error);
      throw error;
    }
  }
};