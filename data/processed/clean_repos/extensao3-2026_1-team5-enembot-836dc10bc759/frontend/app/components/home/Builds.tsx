'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { BUILDS } from '../../lib/catalog';
import type { BuildId } from '../../lib/types';

export function Builds() {
  const [active, setActive] = useState<BuildId>('teorico');
  const activeBuild = BUILDS.find((b) => b.id === active)!;

  return (
    <section className="section" id="builds" style={{ background: 'var(--bg-soft)', borderTop: '1px solid var(--border)' }}>
      <div className="container">
        <motion.div
          className="section-header"
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <span className="eyebrow">
            <span className="eyebrow-dot" /> Builds
          </span>
          <h2 className="section-title">
            Nem todo mundo aprende igual. <em>Escolha seu modo.</em>
          </h2>
          <p className="section-sub">
            Cada build muda o ritmo, a profundidade das explicações e o tipo de questão que cai. Use a que combina
            com seu dia — e troque no meio se quiser.
          </p>
        </motion.div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
          {BUILDS.map((b, idx) => (
            <motion.button
              key={b.id}
              type="button"
              onClick={() => setActive(b.id)}
              aria-pressed={active === b.id}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: idx * 0.08 }}
              style={{
                textAlign: 'left',
                padding: 28,
                borderRadius: 20,
                background: active === b.id ? 'var(--bg-raised)' : 'transparent',
                border: `1px solid ${active === b.id ? 'var(--accent)' : 'var(--border)'}`,
                boxShadow: active === b.id ? 'var(--shadow-glow)' : 'var(--shadow-xs)',
                transition: 'all 220ms cubic-bezier(0.22,1,0.36,1)',
                cursor: 'pointer',
                display: 'flex', flexDirection: 'column', gap: 10,
              }}
            >
              <div
                aria-hidden
                style={{
                  width: 48, height: 48, borderRadius: 12,
                  background: active === b.id ? 'var(--grad-sage)' : 'var(--bg-soft)',
                  display: 'grid', placeItems: 'center', fontSize: 22,
                  color: active === b.id ? 'white' : 'inherit',
                }}
              >
                {b.icon}
              </div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.4rem', fontWeight: 400, letterSpacing: '-0.01em' }}>
                {b.title}
              </div>
              <div style={{
                display: 'inline-flex', padding: '2px 8px', borderRadius: 999,
                background: 'var(--accent-soft)', color: 'var(--accent-strong)',
                fontSize: '0.72rem', fontWeight: 600, width: 'fit-content',
              }}>
                {b.badge}
              </div>
              <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.55 }}>
                {b.description}
              </p>
            </motion.button>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          key={activeBuild.id}
          transition={{ duration: 0.4 }}
          style={{
            marginTop: 32, padding: '22px 26px',
            background: 'var(--bg-raised)', borderRadius: 16,
            border: '1px solid var(--border)',
            display: 'flex', flexDirection: 'column', gap: 12,
          }}
        >
          <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Experimente · {activeBuild.title}
          </div>
          <p style={{ margin: 0, fontSize: '1.05rem', fontStyle: 'italic', fontFamily: 'var(--font-display)' }}>
            "{activeBuild.systemPitch}"
          </p>
          <div style={{ marginTop: 4 }}>
            <Link href="/chat/matematica" className="btn btn-accent">
              Iniciar com {activeBuild.title} →
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
