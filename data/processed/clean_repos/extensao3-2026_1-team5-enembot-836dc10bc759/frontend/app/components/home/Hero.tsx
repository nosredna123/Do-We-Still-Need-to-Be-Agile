'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

export function Hero() {
  return (
    <section className="hero">
      <div className="container hero-inner">
        <motion.div
          className="hero-copy"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          <span className="eyebrow">
            <span className="eyebrow-dot" />
            Tutor de IA para o ENEM
          </span>
          <h1 className="hero-title">
            Estude ENEM do jeito que <em>você</em> aprende —{' '}
            <em className="warm">não como todo mundo</em>.
          </h1>
          <p className="hero-sub">
            Um tutor de IA que se adapta ao seu ritmo, explica do jeito que faz sentido pra
            você e monta o plano de estudo que cabe na sua semana. Escolha uma <strong>build</strong>,
            escolha a matéria, e a gente começa a evoluir junto.
          </p>

          <div className="hero-ctas">
            <Link href="/chat/matematica" className="btn btn-lg btn-primary">
              Começar sessão grátis →
            </Link>
            <a href="#features" className="btn btn-lg btn-ghost">
              Ver recursos
            </a>
          </div>

          <div className="hero-meta">
            <span className="hero-meta-item">
              <span className="dot" /> Sem cadastro para testar
            </span>
            <span className="hero-meta-item">
              <span className="dot" /> 100% adaptativo
            </span>
            <span className="hero-meta-item">
              <span className="dot" /> Feito por estudantes da UECE
            </span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30, rotate: 0 }}
          animate={{ opacity: 1, y: 0, rotate: 0 }}
          transition={{ duration: 0.7, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
        >
          <HeroDemo />
        </motion.div>
      </div>
    </section>
  );
}

function HeroDemo() {
  return (
    <div className="hero-demo" aria-hidden>
      <div className="hero-demo-top">
        <div className="lights">
          <span />
          <span />
          <span />
        </div>
        <span className="title">enembot · sessão de matemática</span>
      </div>
      <div className="hero-demo-body">
        <motion.div
          className="hero-demo-msg ai"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="avatar">E</div>
          <div className="body">
            <div className="who">ENEMBot</div>
            <div>
              Bora começar com <strong>funções do 1º grau</strong>. Vou te mostrar uma questão de 2022.
            </div>
            <div className="hero-demo-question">
              <div className="chips">
                <span className="chip-mini">Funções</span>
                <span className="chip-mini warn">Média</span>
              </div>
              <div className="q-text">
                Uma empresa vende a R$ 25 por unidade. Custos fixos são R$ 1.200 e custo variável R$ 10 por unidade.
                Quantas unidades precisam ser vendidas no mês para lucro zero?
              </div>
              <div className="hero-demo-alts">
                <div className="hero-demo-alt">
                  <span className="letter">A</span> 60 unidades
                </div>
                <div className="hero-demo-alt">
                  <span className="letter">B</span> 70 unidades
                </div>
                <motion.div
                  className="hero-demo-alt correct"
                  initial={{ opacity: 0.4 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.4 }}
                >
                  <span className="letter">C</span> 80 unidades
                </motion.div>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="hero-demo-msg user"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.8 }}
          style={{ justifyContent: 'flex-end' }}
        >
          <div style={{ marginLeft: 'auto' }}>
            <div className="bubble">Resposta C, 80 unidades</div>
          </div>
          <div className="avatar">T</div>
        </motion.div>

        <motion.div
          className="hero-demo-msg ai"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.2 }}
        >
          <div className="avatar">E</div>
          <div className="body">
            <div className="who">ENEMBot</div>
            <div>
              <strong>Correto.</strong> 25x = 1200 + 10x → 15x = 1200 → x = 80. Quer uma variação da mesma questão ou
              subir a dificuldade?
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
