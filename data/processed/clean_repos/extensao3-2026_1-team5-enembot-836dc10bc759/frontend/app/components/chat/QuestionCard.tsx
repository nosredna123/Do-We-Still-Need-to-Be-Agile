'use client';

import type { AlternativeLetter, Question } from '../../lib/types';

type Props = {
  question: Question;
  chosen?: AlternativeLetter;
  feedback?: { correta: boolean; explicacao: string; fixacao?: string[] };
  locked: boolean;
  onChoose: (letter: AlternativeLetter) => void;
};

const DIFF: Record<Question['dificuldade'], { label: string; cls: string }> = {
  facil: { label: 'Fácil', cls: 'accent' },
  media: { label: 'Média', cls: 'warn' },
  dificil: { label: 'Difícil', cls: 'danger' },
};

export function QuestionCard({ question, chosen, feedback, locked, onChoose }: Props) {
  const diff = DIFF[question.dificuldade] ?? DIFF.media;
  const alternativas = question.alternativas.filter((a) => a.texto.trim().length > 0);

  return (
    <article className="q-card q-card--uniform" aria-label="Questão">
      <header className="q-meta">
        <span className="q-chip accent">{question.assunto}</span>
        {question.ano ? <span className="q-chip">ENEM {question.ano}</span> : null}
        <span className={`q-chip ${diff.cls}`}>{diff.label}</span>
      </header>

      <p className="q-statement">{question.enunciado}</p>

      {alternativas.length > 0 ? (
        <ul className="q-alts" role="list">
          {alternativas.map((alt) => {
            const isChosen = chosen === alt.letra;
            let cls = 'q-alt';
            if (locked) {
              if (alt.correta) cls += ' is-correct';
              else if (isChosen && !alt.correta) cls += ' is-wrong';
            } else if (isChosen) {
              cls += ' is-chosen';
            }
            return (
              <li key={alt.letra} className="q-alt-row">
                <button
                  type="button"
                  className={cls}
                  disabled={locked}
                  onClick={() => onChoose(alt.letra)}
                  aria-pressed={isChosen}
                >
                  <span className="letter" aria-hidden>
                    {alt.letra}
                  </span>
                  <span className="q-alt-text">{alt.texto}</span>
                </button>
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="q-empty-alts">Alternativas indisponíveis.</p>
      )}

    </article>
  );
}
