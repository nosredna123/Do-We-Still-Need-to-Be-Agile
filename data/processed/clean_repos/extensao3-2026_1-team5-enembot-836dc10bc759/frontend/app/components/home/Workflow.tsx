'use client';

import { motion } from 'framer-motion';

const steps = [
  {
    n: '01',
    title: 'Escolha matéria e build',
    body:
      'Clique em um dos cinco cards de matéria e decida se a sessão vai ser mais rápida (Estrategista), profunda (Teórico) ou brutal (Sniper).',
  },
  {
    n: '02',
    title: 'Resolva e converse',
    body:
      'A IA serve questões de ENEM reais, comenta cada resposta e te deixa perguntar — com ELI10, aprofundamentos e dicas sem spoiler.',
  },
  {
    n: '03',
    title: 'Construa seu repertório',
    body:
      'Selecione trechos para gerar questões novas, salve flashcards, e deixe o plano semanal se ajustar ao que você erra mais.',
  },
];

export function Workflow() {
  return (
    <section className="section" id="workflow">
      <div className="container">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <span className="eyebrow">
            <span className="eyebrow-dot" /> Como funciona
          </span>
          <h2 className="section-title">
            Em três passos, <em>sem enrolação</em>.
          </h2>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
          {steps.map((s, i) => (
            <motion.div
              key={s.n}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.45, delay: i * 0.1 }}
              style={{
                padding: 28,
                borderRadius: 20,
                border: '1px solid var(--border)',
                background: 'var(--bg-raised)',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <div style={{
                fontFamily: 'var(--font-display)', fontSize: '4rem', lineHeight: 1,
                color: 'var(--accent)', opacity: 0.18,
                position: 'absolute', right: 20, top: 14, letterSpacing: '-0.04em',
              }}>
                {s.n}
              </div>
              <div style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontSize: '0.78rem', marginBottom: 8 }}>
                passo {s.n}
              </div>
              <h3 style={{ margin: '0 0 8px', fontFamily: 'var(--font-display)', fontSize: '1.4rem', fontWeight: 400, letterSpacing: '-0.01em' }}>
                {s.title}
              </h3>
              <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.94rem', lineHeight: 1.55 }}>
                {s.body}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
