'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

export function FinalCTA() {
  return (
    <section className="cta-final">
      <div className="container">
        <motion.div
          className="cta-final-inner"
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2>
            A próxima prova é em breve.<br />
            <em style={{ fontStyle: 'italic' }}>Comece agora.</em>
          </h2>
          <p>
            Sem cadastro, sem plano premium, sem enrolação. Escolha uma matéria e a gente começa.
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, justifyContent: 'center' }}>
            <Link href="/chat/matematica" className="btn btn-lg btn-accent">
              Começar matemática →
            </Link>
            <Link href="/chat/redacao" className="btn btn-lg btn-ghost" style={{ color: 'rgba(255,255,255,0.8)', borderColor: 'rgba(255,255,255,0.2)' }}>
              Treinar redação
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
