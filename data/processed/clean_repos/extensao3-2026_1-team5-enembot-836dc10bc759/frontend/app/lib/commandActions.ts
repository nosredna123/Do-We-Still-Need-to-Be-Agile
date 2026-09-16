import type { CommandActionId } from './llm/llmClient';

export type CommandActionDef = {
  id: CommandActionId;
  label: string;
  description: string;
  icon: string;
  group: 'IA' | 'Navegação' | 'Sessão' | 'Ajustes';
  shortcut?: string;
  /** onde ela aparece (landing, chat, ambos) */
  context: 'global' | 'chat';
};

export const COMMAND_ACTIONS: CommandActionDef[] = [
  // IA — criativas
  {
    id: 'generate-similar',
    label: 'Gerar questão similar',
    description: 'Cria uma variação da questão atual com mesmo nível',
    icon: '✨',
    group: 'IA',
    context: 'chat',
  },
  {
    id: 'explain-eli5',
    label: 'Explicar como se eu tivesse 10 anos',
    description: 'Versão simplificada da explicação, sem jargão',
    icon: '🧒',
    group: 'IA',
    context: 'chat',
  },
  {
    id: 'summarize-topic',
    label: 'Criar resumo do tópico',
    description: 'Sintetiza o conteúdo da questão atual em 4 linhas',
    icon: '📝',
    group: 'IA',
    context: 'chat',
  },
  {
    id: 'flashcards',
    label: 'Gerar flashcards',
    description: 'Cria 5 flashcards de revisão espaçada',
    icon: '🗂️',
    group: 'IA',
    context: 'chat',
  },
  {
    id: 'quiz-topic',
    label: 'Testar meu conhecimento',
    description: 'Mini-quiz de 3 questões sobre o tópico',
    icon: '🎯',
    group: 'IA',
    context: 'chat',
  },
  {
    id: 'simulate-exam',
    label: 'Simular prova relâmpago',
    description: 'Simulado curto com cronômetro',
    icon: '⚡',
    group: 'IA',
    shortcut: '⌘⇧S',
    context: 'chat',
  },
  {
    id: 'open-study-plan',
    label: 'Gerar plano de estudos',
    description: 'Cria um plano semanal com base no seu objetivo',
    icon: '📅',
    group: 'IA',
    shortcut: '⌘⇧P',
    context: 'global',
  },
  {
    id: 'give-hint',
    label: 'Dica sem entregar a resposta',
    description: 'Um empurrãozinho na direção certa',
    icon: '💡',
    group: 'IA',
    shortcut: '⌘.',
    context: 'chat',
  },
  // Navegação / sessão
  {
    id: 'next-question',
    label: 'Próxima questão',
    description: 'Avança para a próxima no banco',
    icon: '→',
    group: 'Sessão',
    shortcut: 'J',
    context: 'chat',
  },
  {
    id: 'start-focus-timer',
    label: 'Iniciar foco (25 min)',
    description: 'Pomodoro para estudar sem distração',
    icon: '⏱',
    group: 'Sessão',
    context: 'chat',
  },
  // Ajustes
  {
    id: 'toggle-theme',
    label: 'Alternar modo claro/escuro',
    description: 'Muda o tema da interface',
    icon: '🌓',
    group: 'Ajustes',
    shortcut: '⌘⇧L',
    context: 'global',
  },
  {
    id: 'switch-build',
    label: 'Trocar build de estudo',
    description: 'Estrategista / Teórico / Sniper',
    icon: '🎮',
    group: 'Ajustes',
    context: 'chat',
  },
];

export const SLASH_COMMANDS = [
  { token: '/proxima', action: 'next-question' as CommandActionId, description: 'Próxima questão', icon: '→' },
  { token: '/dica', action: 'give-hint' as CommandActionId, description: 'Dica discreta', icon: '💡' },
  { token: '/explicar', action: 'explain-eli5' as CommandActionId, description: 'Versão simplificada', icon: '🧒' },
  { token: '/resumo', action: 'summarize-topic' as CommandActionId, description: 'Resumo do tópico', icon: '📝' },
  { token: '/flashcards', action: 'flashcards' as CommandActionId, description: 'Gerar flashcards', icon: '🗂️' },
  { token: '/similar', action: 'generate-similar' as CommandActionId, description: 'Questão similar', icon: '✨' },
  { token: '/quiz', action: 'quiz-topic' as CommandActionId, description: 'Mini-quiz do tópico', icon: '🎯' },
  { token: '/plano', action: 'open-study-plan' as CommandActionId, description: 'Gerar plano de estudos', icon: '📅' },
  { token: '/foco', action: 'start-focus-timer' as CommandActionId, description: 'Iniciar pomodoro 25min', icon: '⏱' },
];
