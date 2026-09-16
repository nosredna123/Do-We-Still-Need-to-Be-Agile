import type { Build, Subject } from './types';

export const BUILDS: Build[] = [
  {
    id: 'estrategista',
    icon: '⏱',
    title: 'Estrategista',
    badge: 'Melhora tempo',
    description:
      'Foco em velocidade e gestao de tempo. Treine com cronometro para resolver mais rapido.',
    systemPitch:
      'Voce tem 2 minutos por questao. Vou te mostrar questoes curtas e cronometrar. Pronto?',
  },
  {
    id: 'teorico',
    icon: '📚',
    title: 'Teorico',
    badge: 'Melhora base',
    description:
      'Foco em compreensao profunda. Receba dicas extras e explicacoes detalhadas.',
    systemPitch:
      'Vamos devagar. A cada questao eu destaco o conceito-chave antes e explico com calma no final.',
  },
  {
    id: 'sniper',
    icon: '🎯',
    title: 'Sniper',
    badge: 'Acerto em dificeis',
    description:
      'Foco em questoes dificeis. Priorize desafios de alto nivel para maximizar acertos.',
    systemPitch:
      'Seleciono so questoes nivel dificil. Errar aqui e aprender - vamos?',
  },
];

export const SUBJECTS: Subject[] = [
  {
    id: 'matematica',
    title: 'Matematica',
    description: 'Funcoes, geometria, estatistica e resolucao de problemas.',
    icon: '📐',
    gradient: 'subject-green',
    accent: '#1ec3a6',
  },
  {
    id: 'linguagens',
    title: 'Linguagens',
    description: 'Interpretacao, literatura, gramatica e texto argumentativo.',
    icon: '📖',
    gradient: 'subject-blue',
    accent: '#5f8bff',
  },
  {
    id: 'natureza',
    title: 'Ciencias da Natureza',
    description: 'Biologia, quimica e fisica com foco em aplicacao pratica.',
    icon: '🧪',
    gradient: 'subject-violet',
    accent: '#9553f3',
  },
  {
    id: 'humanas',
    title: 'Ciencias Humanas',
    description: 'Historia, geografia, filosofia e sociologia.',
    icon: '🌍',
    gradient: 'subject-orange',
    accent: '#f59b22',
  },
  {
    id: 'redacao',
    title: 'Redacao',
    description: 'Dicas e pratica para redacao dissertativa-argumentativa.',
    icon: '✍️',
    gradient: 'subject-pink',
    accent: '#f04383',
  },
];

export function findSubject(id: string): Subject | undefined {
  return SUBJECTS.find((s) => s.id === id);
}

export function findBuild(id: string): Build | undefined {
  return BUILDS.find((b) => b.id === id);
}
