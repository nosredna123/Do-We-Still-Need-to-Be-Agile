import { createContext, useContext, useState, useEffect } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "../../firebase"; // <-- CONFIRME SE ESTE CAMINHO ESTÁ CORRETO
import {
  fetchFlashcards,
  saveFlashcard,
  updateFlashcard as apiUpdateFlashcard,
  deleteFlashcard,
  fetchResumos,
  saveResumo,
  updateResumo as apiUpdateResumo,
  deleteResumo as apiDeleteResumo,
  fetchDicionarios,
  saveDicionario,
  updateDicionario as apiUpdateDicionario,
  deleteDicionario as apiDeleteDicionario,
} from "../services/flashcard.service";

const FlashcardContext = createContext(null);

export const useFlashcards = () => {
  const ctx = useContext(FlashcardContext);
  if (!ctx) throw new Error("useFlashcards must be used within FlashcardProvider");
  return ctx;
};

function groupCardsIntoThemes(cards) {
  const themeMap = {};
  cards.forEach((card) => {
    const name = card.themeName || "Geral";
    if (!themeMap[name]) {
      themeMap[name] = {
        id: name,
        name,
        description: `Cards sobre ${name}`,
        progress: 0,
        cards: [],
      };
    }
    themeMap[name].cards.push({ id: card.id, question: card.question, answer: card.answer });
  });
  return Object.values(themeMap);
}

export const FlashcardProvider = ({ children }) => {
  const [themes, setThemes] = useState([]);
  const [cardsLoading, setCardsLoading] = useState(true);
  const [resumos, setResumos] = useState([]);
  const [dicionarios, setDicionarios] = useState([]);
  const [weeks, setWeeks] = useState([
    { id: 1, title: "Semana 1", days: [] },
    { id: 2, title: "Semana 2", days: [] },
    { id: 3, title: "Semana 3", days: [] },
    { id: 4, title: "Semana 4", days: [] },
  ]);
  const [cardStats, setCardStats] = useState({});
  const [weekLinks, setWeekLinks] = useState([
    { weekId: 1, flashcardIds: [] },
    { weekId: 2, flashcardIds: [] },
    { weekId: 3, flashcardIds: [] },
    { weekId: 4, flashcardIds: [] },
  ]);

  // --- O useEffect ATUALIZADO AQUI ---
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setCardsLoading(true);
        try {
          // Faz todas as requisições em paralelo
          const [cardsData, resumosData, dicionariosData] = await Promise.all([
            fetchFlashcards(),
            fetchResumos(),
            fetchDicionarios(),
          ]);

          // Processa e salva no estado os Flashcards
          setThemes(groupCardsIntoThemes(cardsData));

          // Processa e salva no estado os Resumos
          setResumos(
            resumosData.map((r) => ({
              id: r.id,
              topic: r.topic,
              html: r.html,
              date: new Date(r.createdAt).toLocaleDateString("pt-BR"),
            }))
          );

          // Processa e salva no estado os Dicionários
          setDicionarios(
            dicionariosData.map((d) => ({
              id: d.id,
              topic: d.topic,
              html: d.html,
              termsCount: d.termsCount,
              date: new Date(d.createdAt).toLocaleDateString("pt-BR"),
            }))
          );
        } catch (err) {
          console.error("Erro ao carregar dados do servidor:", err);
        } finally {
          setCardsLoading(false);
        }
      } else {
        // Se o usuário deslogar, limpa os dados
        setThemes([]);
        setResumos([]);
        setDicionarios([]);
        setCardsLoading(false);
      }
    });

    // Limpa o listener ao desmontar o componente
    return () => unsubscribe();
  }, []);
  // ------------------------------------

  const recordAnswer = (cardId, correct) => {
    setCardStats((prev) => {
      const cur = prev[cardId] || { correct: 0, wrong: 0 };
      return {
        ...prev,
        [cardId]: correct
          ? { ...cur, correct: cur.correct + 1 }
          : { ...cur, wrong: cur.wrong + 1 },
      };
    });
  };

  const hasReviewHistory = Object.keys(cardStats).length > 0;

  const getThemePriorities = () => {
    const result = themes.map((theme) => {
      let correct = 0, wrong = 0;
      const wrongCardIds = [];
      theme.cards.forEach((c) => {
        const s = cardStats[c.id];
        if (s) {
          correct += s.correct;
          wrong += s.wrong;
          if (s.wrong > s.correct) wrongCardIds.push(c.id);
        }
      });
      const total = correct + wrong;
      const errorRate = total > 0 ? wrong / total : 0;
      const priority = errorRate >= 0.5 ? "alta" : errorRate >= 0.25 ? "media" : "baixa";
      return { themeId: theme.id, themeName: theme.name, errorRate, totalAttempts: total, wrongCardIds, priority };
    }).filter((t) => t.totalAttempts > 0);
    return result.sort((a, b) => b.errorRate - a.errorRate);
  };

  const addGeneratedCards = async (themeName, cards) => {
    const saved = await Promise.all(
      cards.map((card) =>
        saveFlashcard({ question: card.question, answer: card.answer, themeName })
      )
    );
    const savedCards = saved.map((s) => ({ id: s.id, question: s.question, answer: s.answer }));

    setThemes((prev) => {
      const existing = prev.find((t) => t.name === themeName);
      if (existing) {
        return prev.map((t) =>
          t.name === themeName ? { ...t, cards: [...t.cards, ...savedCards] } : t
        );
      }
      return [
        ...prev,
        {
          id: themeName,
          name: themeName,
          description: `Cards sobre ${themeName}`,
          progress: 0,
          cards: savedCards,
        },
      ];
    });
  };

  const linkCardsToWeek = (weekId, cardIds) => {
    setWeekLinks((prev) =>
      prev.map((wl) =>
        wl.weekId === weekId
          ? { ...wl, flashcardIds: [...new Set([...wl.flashcardIds, ...cardIds])] }
          : wl
      )
    );
  };

  const unlinkCardsFromWeek = (weekId, cardIds) => {
    setWeekLinks((prev) =>
      prev.map((wl) =>
        wl.weekId === weekId
          ? { ...wl, flashcardIds: wl.flashcardIds.filter((id) => !cardIds.includes(id)) }
          : wl
      )
    );
  };

  const getAllCards = () => themes.flatMap((t) => t.cards);

  const getCardsForWeek = (weekId) => {
    const link = weekLinks.find((wl) => wl.weekId === weekId);
    if (!link) return [];
    const allCards = getAllCards();
    if (weekId === 4) return allCards;
    return allCards.filter((c) => link.flashcardIds.includes(c.id));
  };

  const updateWeekDayTopics = (weekId, dayIndex, topics) => {
    setWeeks((prev) =>
      prev.map((w) =>
        w.id === weekId
          ? { ...w, days: w.days.map((d, i) => (i === dayIndex ? { ...d, topics } : d)) }
          : w
      )
    );
  };

  const updateCard = async (cardId, question, answer) => {
    await apiUpdateFlashcard(cardId, { question, answer });
    setThemes((prev) =>
      prev.map((t) => ({
        ...t,
        cards: t.cards.map((c) => (c.id === cardId ? { ...c, question, answer } : c)),
      }))
    );
  };

  const removeCard = async (cardId) => {
    await deleteFlashcard(cardId);
    setThemes((prev) =>
      prev
        .map((t) => ({ ...t, cards: t.cards.filter((c) => c.id !== cardId) }))
        .filter((t) => t.cards.length > 0)
    );
  };

  const renameTheme = async (themeId, newName) => {
    const theme = themes.find((t) => t.id === themeId);
    if (!theme) return;
    await Promise.all(theme.cards.map((card) => apiUpdateFlashcard(card.id, { themeName: newName })));
    setThemes((prev) =>
      prev.map((t) =>
        t.id === themeId
          ? { ...t, id: newName, name: newName, description: `Cards sobre ${newName}` }
          : t
      )
    );
  };

  const deleteTheme = async (themeId) => {
    const theme = themes.find((t) => t.id === themeId);
    if (!theme) return;
    await Promise.all(theme.cards.map((card) => deleteFlashcard(card.id)));
    setThemes((prev) => prev.filter((t) => t.id !== themeId));
  };

  const addResumo = async (topic, html) => {
    const saved = await saveResumo({ topic, html });
    setResumos((prev) => [
      ...prev,
      { id: saved.id, topic: saved.topic, html: saved.html, date: new Date(saved.createdAt).toLocaleDateString("pt-BR") },
    ]);
  };

  const updateResumo = async (id, topic) => {
    await apiUpdateResumo(id, { topic });
    setResumos((prev) => prev.map((r) => r.id === id ? { ...r, topic } : r));
  };

  const removeResumo = async (id) => {
    await apiDeleteResumo(id);
    setResumos((prev) => prev.filter((r) => r.id !== id));
  };

  const addDicionario = async (topic, html, termsCount = 0) => {
    const saved = await saveDicionario({ topic, html, termsCount });
    setDicionarios((prev) => [
      ...prev,
      { id: saved.id, topic: saved.topic, html: saved.html, termsCount: saved.termsCount, date: new Date(saved.createdAt).toLocaleDateString("pt-BR") },
    ]);
  };

  const updateDicionario = async (id, topic) => {
    await apiUpdateDicionario(id, { topic });
    setDicionarios((prev) => prev.map((d) => d.id === id ? { ...d, topic } : d));
  };

  const removeDicionario = async (id) => {
    await apiDeleteDicionario(id);
    setDicionarios((prev) => prev.filter((d) => d.id !== id));
  };

  return (
    <FlashcardContext.Provider
      value={{
        themes, cardsLoading, weeks, weekLinks,
        addGeneratedCards, linkCardsToWeek, unlinkCardsFromWeek,
        getCardsForWeek, getAllCards, updateWeekDayTopics,
        updateCard, removeCard, renameTheme, deleteTheme,
        recordAnswer, cardStats, hasReviewHistory, getThemePriorities,
        resumos, addResumo, updateResumo, removeResumo,
        dicionarios, addDicionario, updateDicionario, removeDicionario,
      }}
    >
      {children}
    </FlashcardContext.Provider>
  );
};