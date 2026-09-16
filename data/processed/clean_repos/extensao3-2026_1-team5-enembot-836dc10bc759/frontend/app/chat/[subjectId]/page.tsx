'use client';

import { notFound } from 'next/navigation';
import { use, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { CommandPalette } from '../../components/chat/CommandPalette';
import { Composer } from '../../components/chat/Composer';
import { HighlightPopover } from '../../components/chat/HighlightPopover';
import { Inspector } from '../../components/chat/Inspector';
import { MessageBubble } from '../../components/chat/MessageBubble';
import { FlashcardsModal } from '../../components/chat/FlashcardsModal';
import { StudyPlanModal } from '../../components/chat/StudyPlanModal';
import { TypingIndicator } from '../../components/chat/TypingIndicator';
import { WorkspaceSidebar } from '../../components/chat/WorkspaceSidebar';
import { useTheme } from '../../components/providers/ThemeProvider';
import {
  createChat,
  deleteChat,
  promptAI,
  promptAIred,
  randomQuestion,
  randomTheme,
  retrieveAllChats,
  retrieveMessagesByChat,
  updateChatStatus,
  updateEssayText,
} from '../../lib/backendApi';
import {
  clearQuestionCache,
  currentQuestionIdFromMessages,
  mapBackendMessages,
  mapBackendMessagesEssay,
  NO_QUESTIONS_AVAILABLE,
  NO_THEMES_AVAILABLE,
} from '../../lib/backendChat';
import { findSubject } from '../../lib/catalog';
import type { ChatSchema } from '../../lib/backendTypes';
import { subjectToHabilidadeId } from '../../lib/subjectHabilidade';
import { buildFixationQuestions, buildQuizPrompt } from '../../lib/llm/studyPrompts';
import type {
  AlternativeLetter,
  ChatMessage,
  Question,
  SmartSuggestion,
  SubjectId,
} from '../../lib/types';
import type { CommandActionId, HighlightAction } from '../../lib/llm/llmClient';

type PageProps = {
  params: Promise<{ subjectId: string }>;
};

export default function ChatPage({ params }: PageProps) {
  const { subjectId: rawSubjectId } = use(params);
  const { setTheme, theme } = useTheme();

  const subject = findSubject(rawSubjectId);
  if (!subject) notFound();

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [typing, setTyping] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);

  const [currentEssayId, setCurrentEssayId] = useState<number | null>(null);
  const currentEssayIdRef = useRef<number | null>(null);


  const [chatId, setChatId] = useState<number | null>(null);
  const [chatStatus, setChatStatus] = useState<0 | 1>(0); // 👈


  const [chats, setChats] = useState<ChatSchema[]>([]);
  const [initError, setInitError] = useState<string | null>(null);

  const [cmdOpen, setCmdOpen] = useState(false);
  const [studyPlanOpen, setStudyPlanOpen] = useState(false);
  const [flashcardsOpen, setFlashcardsOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [pendingDeleteChatId, setPendingDeleteChatId] = useState<number | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const scrollerRef = useRef<HTMLDivElement>(null);
  const rawMessagesRef = useRef<Awaited<ReturnType<typeof retrieveMessagesByChat>>>([]);

  const subjectId = subject.id as SubjectId;
  const habilidadeId = subjectToHabilidadeId(subjectId);
  const chatName = subject.title;

  const subjectChats = useMemo(
    () =>
      chats
        .filter((c) => c.habilidade === habilidadeId)
        .sort((a, b) => {
          const timeA = Date.parse(a.atualizado_em || a.criado_em);
          const timeB = Date.parse(b.atualizado_em || b.criado_em);
          if (timeA !== timeB) return timeB - timeA;
          return b.id - a.id;
        }),
    [chats, habilidadeId],
  );

  const activeChat = useMemo(
    () => subjectChats.find((c) => c.id === chatId) ?? subjectChats[0] ?? null,
    [subjectChats, chatId],
  );

  const scrollToBottom = useCallback(() => {
    const el = scrollerRef.current;
    if (!el) return;
    requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, typing, scrollToBottom]);

  const syncMessages = useCallback(
    async (raw: Awaited<ReturnType<typeof retrieveMessagesByChat>>) => {
      const ordered = [...raw].sort((a, b) => {
        const ta = Date.parse(a.timestamp);
        const tb = Date.parse(b.timestamp);
        if (Number.isNaN(ta) || Number.isNaN(tb)) return a.id - b.id;
        return ta - tb;
      });

      rawMessagesRef.current = ordered;
      const mapped = await mapBackendMessages(ordered, subjectId);
      if (mapped.length === 0) {
        setMessages([
          {
            id: 'no-questions',
            role: 'assistant',
            content: NO_QUESTIONS_AVAILABLE,
            createdAt: Date.now(),
          },
        ]);
        setCurrentQuestion(null);
        return;
      }
      setMessages(mapped);
      const lastQ = [...mapped].reverse().find((m) => m.question)?.question ?? null;
      setCurrentQuestion(lastQ);
    },
    [subjectId],
  );

  const syncEssayMessages = useCallback(
    async (raw: Awaited<ReturnType<typeof retrieveMessagesByChat>>) => {
      rawMessagesRef.current = raw;
      const mapped = await mapBackendMessagesEssay(raw);
  
      console.log('mapped:', JSON.stringify(mapped));
  
      if (mapped.length === 0) {
        setMessages([
          {
            id: 'no-themes',
            role: 'assistant',
            content: NO_THEMES_AVAILABLE,
            createdAt: Date.now(),
          },
        ]);
        setCurrentEssayId(null);
        currentEssayIdRef.current = null;
        return;
      }
      setMessages(mapped);
      const lastEssayId = [...mapped].reverse().find((m) => m.essayId != null)?.essayId ?? null;
      setCurrentEssayId(lastEssayId);
      currentEssayIdRef.current = lastEssayId;
      console.log('currentEssayIdRef atualizado:', currentEssayIdRef.current);
    },
    [],
  );

  const refreshChats = useCallback(async () => {
    const all = await retrieveAllChats();
    setChats(all);
    return all;
  }, []);

  const loadChatHistory = useCallback(
    async (targetChat: ChatSchema) => {
      setChatId(targetChat.id);
      setChatStatus(targetChat.status);

      let raw = await retrieveMessagesByChat(targetChat.id);
      const hasQuestionRef = raw.some((m) => m.question_id != null);
  
      if (raw.length === 0 || (!hasQuestionRef && habilidadeId !== 5)) {
        try {
          raw = habilidadeId === 5
            ? await randomTheme(targetChat.id)
            : await randomQuestion(targetChat.id);
        } catch {
          // mantém raw original
        }
      }
  
      await (habilidadeId === 5 ? syncEssayMessages(raw) : syncMessages(raw));
    },
    [habilidadeId, syncEssayMessages, syncMessages],
  );

  const createNewChat = useCallback(async () => {
    setTyping(true);
    setInitError(null);
    try {
      const nextNumber = subjectChats.length + 1;
      const chat = await createChat(habilidadeId, `${chatName} - Histórico ${nextNumber}`);
      setChats((current) => [chat, ...current]);
      await loadChatHistory(chat);
    } catch (err) {
      setInitError(err instanceof Error ? err.message : 'Falha ao criar um novo histórico');
    } finally {
      setTyping(false);
    }
  }, [chatName, habilidadeId, loadChatHistory, subjectChats.length]);

  const requestDeleteChat = useCallback((targetChatId: number) => {
    setPendingDeleteChatId(targetChatId);
    setDeleteModalOpen(true);
  }, []);

  const confirmDeleteChat = useCallback(
    async (targetChatId: number) => {
      const targetChat = subjectChats.find((c) => c.id === targetChatId);
      if (!targetChat) return;

      setDeleteModalOpen(false);
      setPendingDeleteChatId(null);
      setTyping(true);
      setInitError(null);
      try {
        await deleteChat(targetChatId);
        const remaining = await refreshChats();
        const nextSubjectChats = remaining
          .filter((c) => c.habilidade === habilidadeId)
          .sort((a, b) => {
            const timeA = Date.parse(a.atualizado_em || a.criado_em);
            const timeB = Date.parse(b.atualizado_em || b.criado_em);
            if (timeA !== timeB) return timeB - timeA;
            return b.id - a.id;
          });

        if (nextSubjectChats.length > 0) {
          await loadChatHistory(nextSubjectChats[0]);
          return;
        }

        setChatId(null);
        setMessages([]);
        setCurrentQuestion(null);
        rawMessagesRef.current = [];
        clearQuestionCache();
        const created = await createChat(habilidadeId, `${chatName} - Histórico 1`);
        setChats((current) => [created, ...current]);
        await loadChatHistory(created);
      } catch (err) {
        setInitError(err instanceof Error ? err.message : 'Falha ao excluir o histórico');
      } finally {
        setTyping(false);
      }
    },
    [chatName, habilidadeId, loadChatHistory, refreshChats, subjectChats],
  );

  const cancelDeleteChat = useCallback(() => {
    setDeleteModalOpen(false);
    setPendingDeleteChatId(null);
  }, []);

  const pendingDeleteChat = useMemo(
    () => subjectChats.find((c) => c.id === pendingDeleteChatId) ?? null,
    [pendingDeleteChatId, subjectChats],
  );

  const selectChat = useCallback(
    async (targetChatId: number) => {
      const targetChat = subjectChats.find((c) => c.id === targetChatId);
      if (!targetChat) return;
      setTyping(true);
      setInitError(null);
      try {
        await loadChatHistory(targetChat);
      } catch (err) {
        setInitError(err instanceof Error ? err.message : 'Falha ao carregar o histórico selecionado');
      } finally {
        setTyping(false);
      }
    },
    [loadChatHistory, subjectChats],
  );


  useEffect(() => {
    let cancelled = false;

    setMessages([]);
    setChatId(null);
    setCurrentQuestion(null);
    setCurrentEssayId(null);        // adicionar
    currentEssayIdRef.current = null; // adicionar
    setInitError(null);
    rawMessagesRef.current = [];
    clearQuestionCache();

    (async () => {
      setTyping(true);
      try {
        const allChats = await refreshChats();
        if (cancelled) return;

        const currentSubjectChats = allChats
          .filter((c) => c.habilidade === habilidadeId)
          .sort((a, b) => {
            const timeA = Date.parse(a.atualizado_em || a.criado_em);
            const timeB = Date.parse(b.atualizado_em || b.criado_em);
            if (timeA !== timeB) return timeB - timeA;
            return b.id - a.id;
          });

        if (currentSubjectChats.length > 0) {
          await loadChatHistory(currentSubjectChats[0]);
        } else {
          const created = await createChat(habilidadeId, `${chatName} - Histórico 1`);
          if (cancelled) return;
          setChats((current) => [created, ...current]);
          await loadChatHistory(created);
        }
      } catch (err) {
        if (!cancelled) {
          setInitError(err instanceof Error ? err.message : 'Falha ao conectar ao backend');
        }
      } finally {
        if (!cancelled) setTyping(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [subjectId, habilidadeId, chatName, loadChatHistory, refreshChats, syncMessages, syncEssayMessages]);

  function patchMessage(id: string, patch: Partial<ChatMessage>) {
    setMessages((ms) => ms.map((m) => (m.id === id ? { ...m, ...patch } : m)));
  }

  const questionIdForPrompt = useCallback(() => {
    return currentQuestionIdFromMessages(rawMessagesRef.current, subjectId);
  }, [subjectId]);

  const onChoose = useCallback(
    async (messageId: string, question: Question, letter: AlternativeLetter) => {
      if (!chatId) return;
      patchMessage(messageId, { chosen: letter });
      setTyping(true);
      try {
        const qid = Number(question.id) || questionIdForPrompt();
    
        const raw = await promptAI(chatId, qid, `Alternativa ${letter}`, 1);

        setChatStatus(1)
        const currentChatId = chatId
        await updateChatStatus(currentChatId, 1)

        setChats((current) =>
          current.map((c) => (c.id === currentChatId ? { ...c, status: 1 } : c))
        );

        await syncMessages(raw);
        const alt = question.alternativas.find((a) => a.letra === letter);
        const correta = Boolean(alt?.correta);
        patchMessage(messageId, {
          chosen: letter,
          feedback: {
            correta,
            explicacao: correta ? 'Resposta correta.' : 'Resposta incorreta.',
          },
        });
        patchMessage(messageId, {
          chosen: letter,
          feedback: {
            correta,
            explicacao: correta ? 'Resposta correta.' : 'Resposta incorreta.',
            fixacao: buildFixationQuestions(question, correta),
          },
        });
      } finally {
        setTyping(false);
      }
    },
    [chatId, syncMessages, questionIdForPrompt],
  );

  const onFixationPrompt = useCallback(
    async (prompt: string, questionId?: number) => {
      if (!chatId) return;
      setTyping(true);
      try {
        const qid = questionId && questionId > 0 ? questionId : questionIdForPrompt();
        const raw = await promptAI(chatId, qid, prompt, chatStatus);
        await syncMessages(raw);
      } finally {
        setTyping(false);
      }
    },
    [chatId, questionIdForPrompt, syncMessages],
  );

  const askNext = useCallback(async () => {
    if (!chatId) return;
    setTyping(true);
    try {
      const raw = await randomQuestion(chatId);
      await syncMessages(raw);
      
      setChatStatus(0)
      const currentChatId = chatId;
      await updateChatStatus(currentChatId, 0)
      
      setChats((current) =>
        current.map((c) => (c.id === currentChatId ? { ...c, status: 0 } : c))
      );

    } catch (err) {
      const detail = err instanceof Error ? err.message : '';
      const msg = detail.includes('Nenhuma questão') || detail.includes('matéria')
        ? NO_QUESTIONS_AVAILABLE
        : detail || 'Não foi possível carregar uma nova questão.';
      setMessages((ms) => [
        ...ms,
        {
          id: `sys-${Date.now()}`,
          role: 'system',
          content: msg,
          createdAt: Date.now(),
        },
      ]);
    } finally {
      setTyping(false);
    }
  }, [chatId, syncMessages]);

  const askNextTheme = useCallback(async () => {
    if (!chatId) return;
    setTyping(true);
    try {
      const raw = await randomTheme(chatId);
      await syncEssayMessages(raw);
    } catch (err) {
      const detail = err instanceof Error ? err.message : '';
      const msg = detail.includes('Nenhum tema')
        ? NO_THEMES_AVAILABLE
        : detail || 'Não foi possível carregar um novo tema.';
      setMessages((ms) => [
        ...ms,
        {
          id: `sys-${Date.now()}`,
          role: 'system',
          content: msg,
          createdAt: Date.now(),
        },
      ]);
    } finally {
      setTyping(false);
    }
  }, [chatId, syncEssayMessages]);

  const onSend = useCallback(
    async (text: string, habilidade: string = '') => {
      if (!chatId) return;
      if (/^(proxim|next|seguir|vamos)/i.test(text.trim())) {
        console.log(habilidade);
        await (habilidade === 'redacao' ? askNextTheme() : askNext());
        return;
      }
  
      console.log(text);
      console.log(currentEssayIdRef.current);
      setTyping(true);
      try {
        if (habilidade === 'redacao') {
          const essayId = currentEssayIdRef.current;
          if (!essayId) return;
          const raw = await promptAIred(chatId, essayId, text);
          await syncEssayMessages(raw);
        } else {
          const raw = await promptAI(chatId, questionIdForPrompt(), text, chatStatus);
          await syncMessages(raw);
        }
      } finally {
        setTyping(false);
      }
    },
    [chatId, chatStatus, askNext, askNextTheme, questionIdForPrompt, syncMessages, syncEssayMessages],
  );

  const runCommand = useCallback(
    async (actionId: CommandActionId, habilidade: string = '') => {
      if (actionId === 'generate-similar') {
        await (habilidade === 'redacao' ? askNextTheme() : askNext());
        return;
      }
      if (actionId === 'quiz-topic' && chatId && currentQuestion) {
        setTyping(true);
        try {
          const qid = Number(currentQuestion.id) || questionIdForPrompt();
          const raw = await promptAI(chatId, qid, buildQuizPrompt(currentQuestion, subject.title), chatStatus);
          await syncMessages(raw);
        } finally {
          setTyping(false);
        }
        return;
      }
      if (actionId === 'flashcards') {
        setFlashcardsOpen(true);
        return;
      }
      if (actionId === 'next-question') {
        await (habilidade === 'redacao' ? askNextTheme() : askNext());
        return;
      }
      if (actionId === 'open-study-plan') {
        setStudyPlanOpen(true);
        return;
      }
      if (actionId === 'toggle-theme') {
        setTheme(theme === 'light' ? 'dark' : 'light');
        return;
      }
      const essayId = currentEssayIdRef.current;
      if (!chatId || (!currentQuestion && !essayId)) return;

      setTyping(true);
      try {
        const commandText =
          actionId === 'give-hint'
            ? 'Gerar dica discreta'
            : actionId === 'summarize-topic'
              ? 'Resumo do tópico'
              : actionId === 'explain-eli5'
                ? 'Versão Simplificada'
                : `Comando: ${actionId}`;

        if (currentQuestion) {
          const qid = Number(currentQuestion.id) || questionIdForPrompt();
          const raw = await promptAI(chatId, qid, commandText, chatStatus);
          await syncMessages(raw);
        } else if (essayId) {
          const raw = await promptAIred(chatId, essayId, commandText);
          await syncEssayMessages(raw);
        }
      } finally {
        setTyping(false);
      }
    },
    [askNext, chatId, chatStatus, currentQuestion, questionIdForPrompt, subject.title, syncMessages, syncEssayMessages, setTheme, theme],
  );

  const onSuggestion = useCallback(
    async (s: SmartSuggestion) => {
      if (s.action === 'next' || s.action === 'easier' || s.action === 'harder' || s.action === 'similar') {
        await askNext();
        return;
      }
      if (s.action === 'quiz-topic' && chatId && currentQuestion) {
        setTyping(true);
        try {
          const qid = Number(currentQuestion.id) || questionIdForPrompt();
          const raw = await promptAI(chatId, qid, buildQuizPrompt(currentQuestion, subject.title), chatStatus);
          await syncMessages(raw);
        } finally {
          setTyping(false);
        }
        return;
      }
      if (s.action === 'flashcards') {
        setFlashcardsOpen(true);
        return;
      }
      if (chatId && currentQuestion) {
        setTyping(true);
        try {
          const qid = Number(currentQuestion.id) || questionIdForPrompt();
          const raw = await promptAI(chatId, qid, s.label, chatStatus);
          await syncMessages(raw);
        } finally {
          setTyping(false);
        }
      }
    },
    [askNext, chatId, chatStatus, currentQuestion, questionIdForPrompt,subject.title, syncMessages],
  );

  const onHighlight = useCallback(
    async (selectedText: string, action: HighlightAction) => {
      if (!chatId) return;
      setTyping(true);
      try {
        const raw = await promptAI(chatId, questionIdForPrompt(), `[${action}] ${selectedText}`, chatStatus);
        await syncMessages(raw);
      } finally {
        setTyping(false);
      }
    },
    [chatId, chatStatus, questionIdForPrompt, syncMessages],
  );

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const target = e.target as HTMLElement | null;
      const typingInField =
        target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable);

      // Cmd+B → toggle sidebar
      if ((e.metaKey || e.ctrlKey) && !e.shiftKey && (e.key === 'b' || e.key === 'B')) {
        e.preventDefault();
        setSidebarCollapsed((c) => !c);
        return;
      }
      // Cmd+Shift+L → toggle theme
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === 'l' || e.key === 'L')) {
        e.preventDefault();
        setTheme(theme === 'light' ? 'dark' : 'light');
        return;
      }
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === 'p' || e.key === 'P')) {
        e.preventDefault();
        setStudyPlanOpen(true);
        return;
      }
      if (typingInField) return;
      if (e.key === 'j' || e.key === 'J') askNext();
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [askNext, setTheme, theme]);

  const activeQuestionMessageId = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i];
      if (m.question && !m.feedback) return m.id;
    }
    return null;
  }, [messages]);

  const activeEssayMessageId = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i];
      if (m.essayId && !m.feedback) return m.id;
    }
    return null;
  }, [messages]);

  return (
    <div className={`workspace ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <WorkspaceSidebar
        activeSubjectId={subjectId}
        onOpenCommand={() => setCmdOpen(true)}
        chats={subjectChats}
        selectedChatId={chatId}
        onSelectChat={selectChat}
        onCreateChat={createNewChat}
        onRequestDeleteChat={requestDeleteChat}
        collapsed={sidebarCollapsed}
      />

      <section className="ws-main">
        <div className="ws-topbar">
          <button
            className="icon-btn"
            onClick={() => setSidebarCollapsed((c) => !c)}
            aria-label={sidebarCollapsed ? 'Expandir sidebar (Cmd/Ctrl+B)' : 'Recolher sidebar (Cmd/Ctrl+B)'}
            title={sidebarCollapsed ? 'Expandir (Cmd/Ctrl+B)' : 'Recolher (Cmd/Ctrl+B)'}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M9 3v18" />
            </svg>
          </button>
          <div className="ws-breadcrumb">
            <span>{subject.icon}</span>
            <span className="cur">{subject.title}</span>
            {activeChat && <span className="sep">/</span>}
            {activeChat && <span>{activeChat.chat_name}</span>}
          </div>
          <div className="ws-topbar-actions">
            <button className="icon-btn" onClick={() => setCmdOpen(true)} aria-label="Paleta">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>
            </button>
            <button className="icon-btn" onClick={() => setStudyPlanOpen(true)} aria-label="Plano">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" />
                <path d="M16 2v4M8 2v4M3 10h18" />
              </svg>
            </button>
          </div>
        </div>

        {initError && (
          <div style={{ padding: '12px 16px', color: 'var(--danger, #e11)', fontSize: '0.9rem' }}>
            {initError}
          </div>
        )}

        <div className="ws-scroll" ref={scrollerRef}>
          <div className="ws-stream">
            {messages.map((m) => {
              if (m.role === 'system') {
                return (
                  <div
                    key={m.id}
                    style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem', padding: '6px 0' }}
                  >
                    — {m.content} —
                  </div>
                );
              }
              return (
                <MessageBubble
                  key={m.id}
                  message={m}
                  locked={m.id !== activeQuestionMessageId && m.id !== activeEssayMessageId}
                  onChoose={(l) => m.question && onChoose(m.id, m.question, l)}
                    onFixationPrompt={onFixationPrompt}
                  onSuggestion={onSuggestion}
                  onSubmitEssay={async (essayId, text) => {
                    await updateEssayText(essayId, text)
                    await onSend(text, 'redacao')
                  }}
                  onNext={() => onSend('proxima', 'redacao')}
                />
              );
            })}
            {typing && <TypingIndicator />}
          </div>
        </div>

        <Composer onSend={onSend} onCommand={runCommand} disabled={typing || !chatId}  habilidade={subjectId}/>
      </section>

      <Inspector onOpenStudyPlan={() => setStudyPlanOpen(true)} />

      <CommandPalette open={cmdOpen} onOpenChange={setCmdOpen} onRun={(id) => runCommand(id, subjectId)} scope="chat" />
      <StudyPlanModal
        open={studyPlanOpen}
        onOpenChange={setStudyPlanOpen}
        chatId={chatId}
        questionId={questionIdForPrompt()}
        essayId={currentEssayIdRef.current}
        subjectId={subjectId}
        habilidadeId={habilidadeId}
      />
      <FlashcardsModal
        open={flashcardsOpen}
        onOpenChange={setFlashcardsOpen}
        chatId={chatId}
        chatStatus={chatStatus}
        questionId={questionIdForPrompt()}
        essayId={currentEssayIdRef.current}
        subjectId={subjectId}
        habilidadeId={habilidadeId}
      />
      {deleteModalOpen && pendingDeleteChat && (
        <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="delete-chat-title">
          <div className="modal" style={{ maxWidth: 440, padding: '28px 32px' }}>
            <h2 id="delete-chat-title" style={{ margin: '0 0 12px', fontSize: '1.2rem' }}>
              Excluir histórico
            </h2>
            <p style={{ margin: '0 0 20px', color: 'var(--text-muted)', lineHeight: 1.6 }}>
              Deseja apagar o histórico <strong>{pendingDeleteChat.chat_name || `Conversa #${pendingDeleteChat.id}`}</strong>?
              Essa ação não pode ser desfeita.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <button type="button" className="btn btn-ghost" onClick={cancelDeleteChat}>
                Cancelar
              </button>
              <button type="button" className="btn btn-primary" onClick={() => confirmDeleteChat(pendingDeleteChat.id)}>
                Excluir
              </button>
            </div>
          </div>
        </div>
      )}
      <HighlightPopover containerRef={scrollerRef} onAction={onHighlight} />
    </div>
  );
}
