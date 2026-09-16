'use client';

import { AnimatePresence, motion } from 'framer-motion';
import type { AlternativeLetter, ChatMessage, SmartSuggestion } from '../../lib/types';
import { MessageContent } from './MessageContent';
import { QuestionCard } from './QuestionCard';
import { EssayCard } from './EssayCard';
import { useEffect, useState } from 'react';
import { retrieveEssayById } from '../../lib/backendApi';

type Props = {
  message: ChatMessage;
  locked: boolean;
  onChoose?: (letter: AlternativeLetter) => void;
  onFixationPrompt?: (prompt: string, questionId?: number) => void;
  onSuggestion?: (s: SmartSuggestion) => void;
  onCopy?: () => void;
  onSubmitEssay?: (essayId: number, text: string) => void;
  onNext?: () => void;
};
function formatTime(ts: number) {
  const d = new Date(ts);
  return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function stripGuidedQuestionSuffix(content: string) {
  const lines = content.split(/\r?\n/);
  while (lines.length > 0 && /^\s*~\s*.+/.test(lines[lines.length - 1])) {
    lines.pop();
  }
  return lines.join('\n').trimEnd();
}
function useEssaySubmitted(essayId?: number) {
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (!essayId) return;
    retrieveEssayById(essayId).then((essay) => {
      setSubmitted(essay?.text !== '');
    });
  }, [essayId]);

  return submitted;
}

export function MessageBubble({ message, locked, onChoose, onFixationPrompt, onSuggestion, onCopy, onSubmitEssay, onNext }: Props) {
  const isUser = message.role === 'user';
  const essaySubmitted = useEssaySubmitted(message.essayId);
  const [guidedOpen, setGuidedOpen] = useState(false);
  const fixationItems = message.feedback?.fixacao ?? [];
  console.log(fixationItems)
  const hasGuidedFixation = fixationItems.length > 0;
  const renderedContent = !isUser ? stripGuidedQuestionSuffix(message.content) : message.content;
  console.log("Submetida", essaySubmitted, message.essayId)

  return (
    <>
      <motion.div
        className={`msg ${isUser ? 'user' : 'assistant'}`}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.26, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className={`msg-avatar ${isUser ? 'user' : 'ai'}`} aria-hidden>
          {isUser ? 'T' : 'E'}
        </div>
        <div className="msg-body">
          <div className="msg-header">
            <span className="name">{isUser ? 'Você' : 'ENEMBot'}</span>
            <span className="time">{formatTime(message.createdAt)}</span>
        </div>

 
          {renderedContent && !message.essayId &&(
            <div className="msg-text">
              <MessageContent content={renderedContent} />
            </div>
          )}

          {message.essayId && (
            <div className="msg-question-wrap">
              <EssayCard
                theme={message.content}
                essayId={message.essayId}
                locked={locked || essaySubmitted}
                onSubmit={(essayId, text) => onSubmitEssay?.(essayId, text)}
                onNext={() => onNext?.()}
              />
            </div>
          )}

          {message.question && (
            <div className="msg-question-wrap">
              <QuestionCard
                question={message.question}
                chosen={message.chosen}
                locked={locked || Boolean(message.feedback)}
                onChoose={(l) => onChoose?.(l)}
              />
            </div>
          )}

          {message.feedback?.correta != null && (
            <div className="msg-feedback-shell">
              <div className={`q-verdict ${message.feedback.correta ? 'correct' : 'wrong'}`}>
                <span className="v-icon" aria-hidden>
                  {message.feedback.correta ? '✓' : '✕'}
                </span>
                <div>
                  <strong>{message.feedback.correta ? 'Resposta correta' : ''}</strong>
                  <p className="q-verdict-text">{message.feedback.explicacao}</p>
                  {hasGuidedFixation ? (
                    <button
                      type="button"
                      className="btn btn-ghost q-guided-open"
                      onClick={() => setGuidedOpen(true)}
                    >
                      Abrir fixação guiada
                    </button>
                  ) : null}
                </div>
              </div>
            </div>
          )}

          {message.suggestions && message.suggestions.length > 0 && (
            <div className="suggestions">
              {message.suggestions.map((s) => (
                <button key={s.id} className="suggestion-pill" onClick={() => onSuggestion?.(s)}>
                  {s.icon && (
                    <span className="icon" aria-hidden>
                      {s.icon}
                    </span>
                  )}
                  {s.label}
                </button>
              ))}
            </div>
          )}

          {!isUser && (
            <div className="msg-actions" role="toolbar" aria-label="Ações da mensagem">
              <button
                onClick={() => {
                  void navigator.clipboard.writeText(message.content || '').catch(() => {});
                  onCopy?.();
                }}
                title="Copiar"
                aria-label="Copiar mensagem"
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" />
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                </svg>
              </button>
              <button title="Regenerar" aria-label="Regenerar resposta">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M1 4v6h6M23 20v-6h-6" />
                  <path d="M20.5 9A9 9 0 0 0 5.6 5.6L1 10M23 14l-4.6 4.4A9 9 0 0 1 3.5 15" />
                </svg>
              </button>
              <button title="Bookmark" aria-label="Salvar mensagem">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                </svg>
              </button>
            </div>
          )}
        </div>
      </motion.div>

      <AnimatePresence>
        {guidedOpen && hasGuidedFixation && (
          <>
            <motion.div
              className="modal-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setGuidedOpen(false)}
            />
            <motion.div
              className="modal guided-modal"
              role="dialog"
              aria-modal="true"
              aria-label="Fixação guiada"
              initial={{ opacity: 0, scale: 0.96, y: 8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.98, y: -4 }}
              transition={{ duration: 0.22, ease: [0.34, 1.56, 0.64, 1] }}
            >
              <div className="modal-header guided-header">
                <div>
                  <h3>Fixação guiada</h3>
                  <p className="guided-subtitle">Clique em uma pergunta para reenviar o prompt para a IA.</p>
                </div>
                <button className="icon-btn" onClick={() => setGuidedOpen(false)} aria-label="Fechar">
                  ✕
                </button>
              </div>

              <div className="modal-body guided-body">
                <div className="guided-panel">
                  <div className="guided-panel-copy">
                    <span className="guided-kicker">Perguntas para reflexão</span>
                    <p>
                      Use essas perguntas para revisar o raciocínio.
                    </p>
                  </div>
                  <div className="guided-list">
                    {fixationItems.map((item, index) => (
                      <button
                        key={`${message.id}-guided-${index}`}
                        type="button"
                        className="guided-btn"
                        onClick={() => {
                          onFixationPrompt?.(item, message.questionId);
                          setGuidedOpen(false);
                        }}
                      >
                        <span className="guided-index" aria-hidden>
                          {String(index + 1).padStart(2, '0')}
                        </span>
                        <span className="guided-text">{item}</span>
                        <span className="guided-arrow" aria-hidden>
                          →
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="modal-footer guided-footer">
                <button className="btn btn-ghost" onClick={() => setGuidedOpen(false)}>
                  Fechar
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
