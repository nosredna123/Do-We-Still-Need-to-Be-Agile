'use client';

import { motion } from 'framer-motion';

const fade = {
  initial: { opacity: 0, y: 16 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-80px' },
  transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] as const },
};

export function Features() {
  return (
    <section className="section" id="features">
      <div className="container">
        <motion.div className="section-header" {...fade}>
          <span className="eyebrow">
            <span className="eyebrow-dot" /> Por que ENEMBot
          </span>
          <h2 className="section-title">
            Tudo que um cursinho caro promete, <em style={{ fontStyle: 'italic' }}>sem a mensalidade</em>.
          </h2>
          <p className="section-sub">
            Um workspace de estudo que combina chat com IA, questões reais de ENEM, revisão espaçada e
            acompanhamento de progresso — tudo em uma interface que você vai querer abrir todo dia.
          </p>
        </motion.div>

        <div className="bento">
          <motion.article className="bento-cell span-4" {...fade}>
            <div className="cell-eyebrow">Builds de estudo</div>
            <h3>Escolha o jeito que seu cérebro aprende hoje.</h3>
            <p>
              Três modos curados: <strong>Estrategista</strong> pra treinar velocidade, <strong>Teórico</strong> pra
              entender o porquê e <strong>Sniper</strong> pra encarar as difíceis. Troque no meio da sessão.
            </p>
            <div className="cell-visual">
              <div className="fi-builds" style={{ padding: '16px 28px 24px' }}>
                <div className="fi-build">
                  <div className="icon">⏱</div>
                  <div className="label">Estrategista</div>
                </div>
                <div className="fi-build">
                  <div className="icon">📚</div>
                  <div className="label">Teórico</div>
                </div>
                <div className="fi-build">
                  <div className="icon">🎯</div>
                  <div className="label">Sniper</div>
                </div>
              </div>
            </div>
          </motion.article>

          <motion.article className="bento-cell span-2" {...fade}>
            <div className="cell-eyebrow">⌘K</div>
            <h3>Comandos em um toque.</h3>
            <p>
              Paleta de comandos estilo Raycast: gere questões, cria flashcards, resume um tópico — tudo sem sair
              da tela.
            </p>
            <div className="cell-visual">
              <div style={{ padding: '16px 28px 24px' }}>
                <div className="fi-slash">
                  <div>
                    <span className="cmd">/flashcards</span> — gerar cartões
                  </div>
                  <div>
                    <span className="cmd">/similar</span> — questão parecida
                  </div>
                  <div>
                    <span className="cmd">/explicar</span> — ELI10
                  </div>
                  <div className="hint">Digite "/" no chat ou ⌘K em qualquer lugar</div>
                </div>
              </div>
            </div>
          </motion.article>

          <motion.article className="bento-cell span-3" {...fade}>
            <div className="cell-eyebrow">Atalhos do chat</div>
            <h3>Faça mais sem tirar as mãos do fluxo.</h3>
            <p>
              Comandos rápidos para abrir a paleta, avançar a sessão e alternar o foco sem sair da conversa.
              Menos cliques, mais estudo.
            </p>
            <div className="cell-visual">
              <div style={{ padding: '20px 28px 24px' }}>
                <div className="fi-slash">
                  <div>
                    <span className="cmd">⌘K</span> — abrir comandos
                  </div>
                  <div>
                    <span className="cmd">J</span> — próxima questão
                  </div>
                  <div>
                    <span className="cmd">⌘B</span> — recolher sidebar
                  </div>
                </div>
              </div>
            </div>
          </motion.article>

          <motion.article className="bento-cell span-3" {...fade}>
            <div className="cell-eyebrow">Plano personalizado</div>
            <h3>Diga sua meta — ganha um plano semanal.</h3>
            <p>
              "Faltam 60 dias, quero focar em exatas." Pronto. A IA monta uma semana com blocos de conteúdo novo,
              revisão espaçada e redação no domingo.
            </p>
            <div className="cell-visual">
              <div className="fi-progress" style={{ padding: '20px 28px 24px' }}>
                {[1, 3, 2, 4, 3, 2, 4].map((l, i) => (
                  <div key={i} className={`day l${l}`} />
                ))}
              </div>
            </div>
          </motion.article>

          <motion.article className="bento-cell span-3" {...fade}>
            <div className="cell-eyebrow">Selecione e pergunte</div>
            <h3>Qualquer palavra pode virar uma aula.</h3>
            <p>
              Selecione um trecho da explicação, do enunciado ou de qualquer mensagem. Um popover aparece com
              ações de IA: <em style={{ fontStyle: 'italic' }}>explicar</em>, <em style={{ fontStyle: 'italic' }}>aprofundar</em>, <em style={{ fontStyle: 'italic' }}>gerar questão</em>.
            </p>
            <div className="cell-visual">
              <div style={{ padding: '16px 28px 24px', position: 'relative' }}>
                <div style={{
                  padding: '12px 14px', background: 'var(--bg)', border: '1px solid var(--border)',
                  borderRadius: 10, fontSize: '0.86rem', lineHeight: 1.5, position: 'relative',
                }}>
                  O ponto de equilíbrio ocorre quando <span style={{ background: 'var(--accent-soft)', padding: '1px 4px', borderRadius: 3 }}>Receita = Custo Total</span>, isto é…
                  <div style={{
                    position: 'absolute', top: -30, right: 20,
                    background: 'var(--bg-inverted)', color: 'var(--text-inverted)',
                    padding: '4px', borderRadius: 8, display: 'flex', gap: 2,
                    fontSize: '0.72rem', boxShadow: 'var(--shadow-lg)',
                  }}>
                    <span style={{ padding: '4px 8px' }}>💬 Explicar</span>
                    <span style={{ padding: '4px 8px' }}>🔬 Aprofundar</span>
                    <span style={{ padding: '4px 8px' }}>✨ Gerar questão</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.article>

          <motion.article className="bento-cell span-3" {...fade}>
            <div className="cell-eyebrow">Revisão espaçada</div>
            <h3>Não esqueça o que aprendeu ontem.</h3>
            <p>
              Cada acerto entra em uma fila de revisão com intervalos crescentes. A lembrança fica firme sem
              você precisar criar cartões à mão.
            </p>
            <div className="cell-visual">
              <div style={{ padding: '20px 28px 24px' }}>
                <div className="queue-item">
                  <span className="date">Hoje</span>
                  <span className="subj">Regra de três composta</span>
                  <span className="badge-mini">3d</span>
                </div>
                <div className="queue-item">
                  <span className="date">Hoje</span>
                  <span className="subj">Metáfora × metonímia</span>
                  <span className="badge-mini">1d</span>
                </div>
                <div className="queue-item" style={{ opacity: 0.7 }}>
                  <span className="date">Amanhã</span>
                  <span className="subj">Guerra Fria</span>
                  <span className="badge-mini">5d</span>
                </div>
              </div>
            </div>
          </motion.article>
        </div>
      </div>
    </section>
  );
}
