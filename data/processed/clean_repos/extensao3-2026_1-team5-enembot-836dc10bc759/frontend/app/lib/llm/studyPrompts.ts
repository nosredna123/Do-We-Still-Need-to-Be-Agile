import type { Question } from '../types';

function basePrompt(question: Question, subjectTitle: string, outcome: 'correct' | 'wrong') {
  const outcomeLabel = outcome === 'correct' ? 'acerto' : 'erro';
  const focus =
    outcome === 'correct'
      ? 'fixação, transferência e reflexão'
      : 'revisão do raciocínio, recuperação do conceito e reflexão sobre a armadilha';

  return [
    'Gere perguntas adicionais para estudo e fixação em português do Brasil.',
    `Tema: ${subjectTitle}`,
    `Assunto da questão: ${question.assunto}`,
    `Enunciado: ${question.enunciado}`,
    `Explicação da questão: ${question.explicacao}`,
    `Situação: ${outcomeLabel}`,
    `Objetivo: ${focus}`,
    'Regras de saída:',
    '- responda somente com 3 perguntas curtas e diretas',
    '- use markdown com uma lista numerada',
    '- não responda as perguntas',
    '- não repita o enunciado da questão',
    '- a terceira pergunta deve ser de reflexão/aplicação',
    'Se for útil, inclua um tom de estudo leve e encorajador.',
  ].join('\n');
}

export function buildFixationPrompt(question: Question, subjectTitle: string, correct: boolean) {
  return basePrompt(question, subjectTitle, correct ? 'correct' : 'wrong');
}

export function buildQuizPrompt(question: Question, subjectTitle: string) {
  return [
    'Gere um mini-quiz de fixação em português do Brasil.',
    `Tema: ${subjectTitle}`,
    `Assunto da questão: ${question.assunto}`,
    'Regras de saída:',
    '- responda somente com 3 perguntas curtas e diretas',
    '- use markdown com uma lista numerada',
    '- não responda as perguntas',
    '- a terceira pergunta deve exigir reflexão ou aplicação',
  ].join('\n');
}

export function buildFixationQuestions(question: Question, correct: boolean): string[] {
  const first = correct
    ? 'Qual foi o principal insight necessário para resolver esta questão?'
    : 'Qual conceito ou interpretação mais contribuiu para o erro nesta questão?';

  const second = correct
    ? 'Em que outro tipo de situação esse mesmo raciocínio pode ser aplicado?'
    : 'Como reconhecer esse mesmo padrão antes de cometer o erro novamente?';

  const third = correct
    ? 'O que torna esta questão diferente de outras parecidas?'
    : 'Qual sinal poderia indicar mais cedo que o caminho escolhido estava incorreto?';

  return [first, second, third];
}