'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { SUBJECTS } from '../../lib/catalog';

export function SubjectsShowcase() {
  return (
    <section className="section" style={{ paddingTop: 20 }}>
      <div className="container">
        <motion.div
          className="section-header"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <span className="eyebrow">
            <span className="eyebrow-dot" /> Matérias
          </span>
          <h2 className="section-title">
            Comece por <em style={{ fontStyle: 'italic' }}>onde doer mais</em>.
          </h2>
          <p className="section-sub">Cinco áreas do ENEM, cada uma com banco próprio e tutor calibrado.</p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
          {SUBJECTS.map((s, i) => (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.06 }}
            >
              <Link
                href={`/chat/${s.id}`}
                style={{
                  display: 'block',
                  padding: 22,
                  borderRadius: 16,
                  background: 'var(--bg-raised)',
                  border: '1px solid var(--border)',
                  transition: 'all 220ms cubic-bezier(0.22,1,0.36,1)',
                  position: 'relative', overflow: 'hidden',
                }}
                className="subject-tile"
              >
                <div
                  aria-hidden
                  style={{
                    width: 44, height: 44, borderRadius: 12,
                    display: 'grid', placeItems: 'center',
                    fontSize: 22, marginBottom: 12,
                    color: 'white',
                    background:
                      s.gradient === 'subject-green'
                        ? 'linear-gradient(145deg, #1ec3a6, #0fb58f)'
                        : s.gradient === 'subject-blue'
                          ? 'linear-gradient(145deg, #5f8bff, #3a65e9)'
                          : s.gradient === 'subject-violet'
                            ? 'linear-gradient(145deg, #9553f3, #7944ea)'
                            : s.gradient === 'subject-orange'
                              ? 'linear-gradient(145deg, #f59b22, #ee7b0f)'
                              : 'linear-gradient(145deg, #f04383, #dd2c6d)',
                  }}
                >
                  {s.icon}
                </div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', fontWeight: 400, letterSpacing: '-0.01em', marginBottom: 6 }}>
                  {s.title}
                </div>
                <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.5 }}>
                  {s.description}
                </p>
                <div style={{ marginTop: 14, color: 'var(--accent)', fontSize: '0.84rem', fontWeight: 500 }}>
                  Iniciar sessão →
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
