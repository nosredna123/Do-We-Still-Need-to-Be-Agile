'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useMemo, useState } from 'react';
import { promptAI, promptAIred } from '../../lib/backendApi';
import { mapBackendMessages } from '../../lib/backendChat';
import type { SubjectId } from '../../lib/types';

type Flashcard = {
  front: string;
  back: string;
};

const FLASHCARD_COUNT = 4;

const FLASHCARD_STYLES = [
  'Use analogias curtas e um exemplo cotidiano diferente do habitual.',
  'Mude a ordem da explicação e priorize uma definição direta no verso.',
  'Traga uma dica de memorização breve e uma armadilha comum no ENEM.',
  'Prefira uma formulação mais objetiva e variada, sem repetir frases padrão.',
];

type Props = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  chatId?: number | null;
  chatStatus: 0 | 1;
  questionId?: number;
  essayId: number | null;
  subjectId?: SubjectId;
  habilidadeId?: number
};

function parseFlashcards(reply: string): Flashcard[] {
  const blocks = reply
    .split(/\n\s*---\s*\n/g)
    .map((block) => block.trim())
    .filter(Boolean);

  const cards = blocks
    .map((block) => {
      const lines = block
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean);

      const frontLine = lines.find((line) => /^Q[:\-]/i.test(line));
      const backLine = lines.find((line) => /^A[:\-]/i.test(line));
      const front = frontLine ? frontLine.replace(/^Q[:\-]\s*/i, '').trim() : '';
      const back = backLine ? backLine.replace(/^A[:\-]\s*/i, '').trim() : '';

      return front && back ? { front, back } : null;
    })
    .filter((card): card is Flashcard => Boolean(card));

  return cards;
}

export function FlashcardsModal({ open, onOpenChange, chatId, chatStatus, questionId = 0, essayId = 0, subjectId = 'matematica', habilidadeId=1 }: Props) {
  const [topic, setTopic] = useState('');
  const [reply, setReply] = useState<string | null>(null);
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const visibleCards = useMemo(() => flashcards.slice(0, FLASHCARD_COUNT), [flashcards]);

  async function generate() {
    if (!chatId) {
      setError('Abra um chat de matéria para gerar flashcards.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const styleHint = FLASHCARD_STYLES[Math.floor(Math.random() * FLASHCARD_STYLES.length)];
      const variationSeed = Math.random().toString(36).slice(2, 8);
      const prompt = [
        'Crie flashcards em markdown.',
        'Formato obrigatório para cada cartão:',
        'Q: pergunta curta',
        'A: resposta objetiva e didática',
        'Separe cada cartão com uma linha contendo ---',
        `Quantidade de cartões: ${FLASHCARD_COUNT}`,
        'Crie exatamente 4 cartões.',
        `Varie a ordem e a formulação nesta tentativa (${variationSeed}).`,
        `Estilo desta rodada: ${styleHint}`,
        topic ? `Tema principal: ${topic}` : 'Tema principal: a questão ou tópico em andamento',
      ].join(' ');

      const raw =
      habilidadeId === 5 && essayId
        ? await promptAIred(chatId, essayId, prompt)
        : await promptAI(chatId, questionId, prompt, chatStatus);
      const mapped = await mapBackendMessages(raw, subjectId);
      const lastLlm = [...mapped].reverse().find((m) => m.role === 'assistant' && m.content);
      const text = lastLlm?.content ?? 'A IA não retornou texto. Tente de novo no chat.';
      const parsed = parseFlashcards(text).slice(0, FLASHCARD_COUNT);
      setReply(text);
      setFlashcards(
        parsed
          .map((card) => ({ card, sort: Math.random() }))
          .sort((a, b) => a.sort - b.sort)
          .map(({ card }) => card),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao chamar a API');
      setReply(null);
      setFlashcards([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="modal-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => onOpenChange(false)}
          />
          <motion.div
            className="modal flashcards-modal"
            role="dialog"
            aria-modal="true"
            aria-label="Flashcards via IA"
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.98, y: -4 }}
            transition={{ duration: 0.22, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <div className="modal-header flashcards-header">
              <div>
                <h3>🗂️ Flashcards (IA)</h3>
                <p className="flashcards-subtitle">Cartões curtos, front/back, com foco em revisão espaçada.</p>
              </div>
              <button className="icon-btn" onClick={() => onOpenChange(false)} aria-label="Fechar">
                ✕
              </button>
            </div>

            <div className="modal-body flashcards-body">
              {!reply ? (
                <div className="flashcards-form">
                  {!chatId && (
                    <p className="flashcards-note flashcards-note-danger">
                      Entre em um chat de matéria antes de gerar flashcards.
                    </p>
                  )}

                  <div className="flashcards-hero">
                    <div className="flashcards-hero-copy">
                      <span className="flashcards-hero-kicker">Revisão ativa</span>
                      <h4>Transforme o assunto em cartões mais limpos e mais fáceis de revisar.</h4>
                      <p>
                        Cada cartão vem com frente e verso, então você pode revisar o ponto-chave sem virar um bloco de texto.
                      </p>
                    </div>
                    <div className="flashcards-hero-deck" aria-hidden>
                      <div className="flashcard-preview preview-1" />
                      <div className="flashcard-preview preview-2" />
                      <div className="flashcard-preview preview-3" />
                    </div>
                  </div>

                  <label className="flashcards-field">
                    <span>Tema dos cartões</span>
                    <input
                      className="input"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="Ex.: Funções, probabilidade, interpretação de texto..."
                    />
                  </label>

                  <div className="flashcards-grid-config">
                    <label className="flashcards-field">
                      <span>Quantidade</span>
                      <input className="input" value={FLASHCARD_COUNT} disabled readOnly />
                    </label>
                  </div>

                  {error && <p className="flashcards-note flashcards-note-danger">{error}</p>}
                </div>
              ) : (
                <div className="flashcards-result">
                  <div className="flashcards-results-head">
                    <div>
                      <span className="flashcards-hero-kicker">Deck gerado</span>
                      <h4>{visibleCards.length} cartões prontos para revisar</h4>
                    </div>
                    <button className="btn btn-ghost" onClick={() => setReply(null)}>
                      Novo deck
                    </button>
                  </div>

                  <div className="flashcards-deck">
                    {visibleCards.length > 0 ? (
                      visibleCards.map((card, index) => (
                        <article key={`${card.front}-${index}`} className="flashcard">
                          <div className="flashcard-label">{String(index + 1).padStart(2, '0')}</div>
                          <div className="flashcard-face flashcard-front">
                            <span className="flashcard-face-title">Frente</span>
                            <p>{card.front}</p>
                          </div>
                          <div className="flashcard-face flashcard-back">
                            <span className="flashcard-face-title">Verso</span>
                            <p>{card.back}</p>
                          </div>
                        </article>
                      ))
                    ) : (
                      <div className="flashcards-empty">
                        <p>Não consegui separar os cartões automaticamente.</p>
                        <pre>{reply}</pre>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer flashcards-footer">
              <button className="btn btn-ghost" onClick={() => onOpenChange(false)}>
                Cancelar
              </button>
              <button className="btn btn-accent" onClick={generate} disabled={loading || !chatId}>
                {loading ? 'Montando deck…' : reply ? 'Gerar outro deck' : 'Gerar flashcards'}
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}