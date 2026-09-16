'use client';

import { motion } from 'framer-motion';

const quotes = [
  {
    quote:
      'Finalmente um chat que não parece o ChatGPT. Os atalhos e o painel lateral me fazem estudar 30% mais rápido — e eu REALMENTE volto todo dia.',
    author: 'Beatriz · 3º ano, Fortaleza',
  },
  {
    quote:
      'O Modo Teórico explica o porquê antes da resposta. Isso foi o que destravou geometria espacial pra mim — ninguém tinha explicado assim.',
    author: 'João · pretendente Medicina',
  },
  {
    quote:
      'Selecionar o texto e pedir pra aprofundar virou meu atalho favorito. Salvei 40+ flashcards em uma semana sem esforço.',
    author: 'Mariana · cursinho popular UECE',
  },
];

export function Testimonials() {
  return (
    <section className="section" style={{ paddingTop: 40 }}>
      <div className="container">
        <motion.div
          className="section-header"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <span className="eyebrow">
            <span className="eyebrow-dot" /> Quem usa
          </span>
          <h2 className="section-title">
            Feito por estudantes <em style={{ fontStyle: 'italic' }}>pra</em> estudantes.
          </h2>
          <p className="section-sub">
            Não somos cursinho. Somos um grupo da UECE que quis construir a ferramenta de estudo que a gente
            gostaria de ter usado.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
          {quotes.map((q, i) => (
            <motion.figure
              key={q.author}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              style={{
                margin: 0, padding: 26,
                border: '1px solid var(--border)', borderRadius: 18,
                background: 'var(--bg-raised)',
                display: 'flex', flexDirection: 'column', gap: 14,
              }}
            >
              <span aria-hidden style={{ fontFamily: 'var(--font-display)', fontSize: '2.8rem', lineHeight: 0.8, color: 'var(--accent)', opacity: 0.6 }}>
                "
              </span>
              <blockquote style={{ margin: 0, fontSize: '1rem', lineHeight: 1.55, color: 'var(--text-primary)' }}>
                {q.quote}
              </blockquote>
              <figcaption style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>— {q.author}</figcaption>
            </motion.figure>
          ))}
        </div>
      </div>
    </section>
  );
}
