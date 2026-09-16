'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useState } from 'react';
import { promptAI, promptAIred } from '../../lib/backendApi';
import { mapBackendMessages } from '../../lib/backendChat';
import type { SubjectId } from '../../lib/types';

type Props = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  /** Obrigatório para chamar a IA real (PUT /chat/prompt). */
  chatId?: number | null;
  questionId?: number;
  essayId: number | null
  subjectId?: SubjectId;
  habilidadeId?: number;
};

export function StudyPlanModal({
  open,
  onOpenChange,
  chatId,
  questionId = 0,
  essayId,
  subjectId = 'matematica',
  habilidadeId = 1,
}: Props) {
  const [goal, setGoal] = useState('Faltam 60 dias para o ENEM, quero focar em exatas.');
  const [minutes, setMinutes] = useState(60);
  const [days, setDays] = useState(7);
  const [reply, setReply] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    if (!chatId) {
      setError('Abra uma matéria no chat para a IA gerar o plano (API /chat/prompt).');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const texto = [
        'Monte um plano de estudos em markdown.',
        `Objetivo: ${goal}`,
        `Minutos por dia: ${minutes}`,
        `Dias: ${days}`,
      ].join(' ');
      const raw =
      habilidadeId === 5 && essayId
        ? await promptAIred(chatId, essayId, texto)
        : await promptAI(chatId, questionId, texto, 1);
      const mapped = await mapBackendMessages(raw, subjectId);
      const lastLlm = [...mapped].reverse().find((m) => m.role === 'assistant' && m.content);
      setReply(lastLlm?.content ?? 'A IA não retornou texto. Tente de novo no chat.');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao chamar a API');
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
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label="Plano de estudos via IA"
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.98, y: -4 }}
            transition={{ duration: 0.22, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <div className="modal-header">
              <h3>📅 Plano de estudos (IA)</h3>
              <button className="icon-btn" onClick={() => onOpenChange(false)} aria-label="Fechar">
                ✕
              </button>
            </div>
            <div className="modal-body">
              {!reply ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {!chatId && (
                    <p style={{ color: 'var(--danger, #e11)', fontSize: '0.88rem', margin: 0 }}>
                      Entre em um chat de matéria antes de gerar — a IA só responde pela API do backend.
                    </p>
                  )}
                  <label style={{ fontSize: '0.86rem', color: 'var(--text-secondary)' }}>
                    Objetivo
                    <textarea
                      value={goal}
                      onChange={(e) => setGoal(e.target.value)}
                      className="input textarea"
                      style={{ marginTop: 6 }}
                    />
                  </label>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                    <label style={{ fontSize: '0.86rem', color: 'var(--text-secondary)' }}>
                      Min/dia
                      <input
                        type="number"
                        className="input"
                        value={minutes}
                        min={15}
                        onChange={(e) => setMinutes(Number(e.target.value) || 60)}
                        style={{ marginTop: 6 }}
                      />
                    </label>
                    <label style={{ fontSize: '0.86rem', color: 'var(--text-secondary)' }}>
                      Dias
                      <input
                        type="number"
                        className="input"
                        value={days}
                        min={3}
                        max={14}
                        onChange={(e) => setDays(Number(e.target.value) || 7)}
                        style={{ marginTop: 6 }}
                      />
                    </label>
                  </div>
                  {error && <p style={{ color: 'var(--danger, #e11)', fontSize: '0.85rem' }}>{error}</p>}
                </div>
              ) : (
                <div className="msg-text" style={{ fontSize: '0.92rem' }}>
                  <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>{reply}</pre>
                </div>
              )}
            </div>
            <div className="modal-footer">
              {reply ? (
                <>
                  <button className="btn btn-ghost" onClick={() => setReply(null)}>
                    Novo pedido
                  </button>
                  <button className="btn btn-accent" onClick={() => onOpenChange(false)}>
                    Fechar
                  </button>
                </>
              ) : (
                <>
                  <button className="btn btn-ghost" onClick={() => onOpenChange(false)}>
                    Cancelar
                  </button>
                  <button className="btn btn-accent" onClick={generate} disabled={loading || !chatId}>
                    {loading ? 'Chamando API…' : 'Gerar com IA'}
                  </button>
                </>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
