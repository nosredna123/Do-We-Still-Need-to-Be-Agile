import type { Difficulty, Question, SubjectId } from './types';

/**
 * Banco de questoes mockadas. Serve o prototipo ponta-a-ponta sem LLM real.
 *
 * Quando o LLM for plugado em mockLlmClient.ts, o client pode:
 *  (a) buscar questao oficial aqui via pickQuestion(); ou
 *  (b) gerar nova com IA e salvar em 'questao' com origem='gerada_ia'.
 */

const QUESTIONS: Question[] = [
  // -------- MATEMATICA --------
  {
    id: 'mat-01',
    subjectId: 'matematica',
    assunto: 'Funcoes',
    ano: 2022,
    dificuldade: 'media',
    enunciado:
      'Uma empresa vende um produto por R$ 25,00 a unidade. Os custos fixos mensais sao de R$ 1.200,00 e o custo variavel por unidade e R$ 10,00. Quantas unidades precisam ser vendidas em um mes para que a empresa atinja o ponto de equilibrio (lucro zero)?',
    alternativas: [
      { letra: 'A', texto: '60 unidades', correta: false, feedback: 'Isso daria receita menor que o custo total.' },
      { letra: 'B', texto: '70 unidades', correta: false, feedback: 'Ainda falta cobrir os custos fixos.' },
      { letra: 'C', texto: '80 unidades', correta: true, feedback: 'Exato: 80 x (25 - 10) = 1.200.' },
      { letra: 'D', texto: '100 unidades', correta: false, feedback: 'Essa venda ja gera lucro positivo.' },
      { letra: 'E', texto: '120 unidades', correta: false, feedback: 'Acima do ponto de equilibrio.' },
    ],
    explicacao:
      'O ponto de equilibrio ocorre quando Receita = Custo Total. Receita = 25x, Custo = 1200 + 10x. Igualando: 25x = 1200 + 10x → 15x = 1200 → x = 80.',
  },
  {
    id: 'mat-02',
    subjectId: 'matematica',
    assunto: 'Probabilidade',
    ano: 2021,
    dificuldade: 'facil',
    enunciado:
      'Em uma urna ha 3 bolas vermelhas e 5 bolas azuis. Retirando uma bola ao acaso, qual a probabilidade de sair uma bola vermelha?',
    alternativas: [
      { letra: 'A', texto: '1/8', correta: false },
      { letra: 'B', texto: '3/8', correta: true, feedback: 'Correto: 3 favoraveis em 8 possiveis.' },
      { letra: 'C', texto: '3/5', correta: false },
      { letra: 'D', texto: '5/8', correta: false, feedback: 'Essa e a probabilidade de sair azul.' },
      { letra: 'E', texto: '1/2', correta: false },
    ],
    explicacao: 'P(vermelha) = casos favoraveis / total = 3 / (3+5) = 3/8.',
  },
  {
    id: 'mat-03',
    subjectId: 'matematica',
    assunto: 'Geometria',
    ano: 2019,
    dificuldade: 'dificil',
    enunciado:
      'Um cilindro reto tem raio da base igual a 4 cm e altura igual a 10 cm. Qual o seu volume, em cm3? (Use π ≈ 3,14)',
    alternativas: [
      { letra: 'A', texto: '125,6', correta: false },
      { letra: 'B', texto: '251,2', correta: false },
      { letra: 'C', texto: '376,8', correta: false },
      { letra: 'D', texto: '502,4', correta: true, feedback: 'Isso: V = π r² h = 3,14 · 16 · 10.' },
      { letra: 'E', texto: '1005,0', correta: false },
    ],
    explicacao: 'V = π r² h = 3,14 × 4² × 10 = 3,14 × 16 × 10 = 502,4 cm³.',
  },

  // -------- LINGUAGENS --------
  {
    id: 'ling-01',
    subjectId: 'linguagens',
    assunto: 'Figuras de linguagem',
    ano: 2020,
    dificuldade: 'facil',
    enunciado:
      '"Minha boca e um tumulo." O recurso estilistico predominante na frase acima e:',
    alternativas: [
      { letra: 'A', texto: 'Hiperbole', correta: false },
      { letra: 'B', texto: 'Metafora', correta: true, feedback: 'Sim: comparacao implicita entre boca e tumulo.' },
      { letra: 'C', texto: 'Metonimia', correta: false },
      { letra: 'D', texto: 'Antitese', correta: false },
      { letra: 'E', texto: 'Ironia', correta: false },
    ],
    explicacao:
      'Metafora e uma comparacao implicita. "Boca e tumulo" associa silencio a fechamento absoluto sem usar "como".',
  },
  {
    id: 'ling-02',
    subjectId: 'linguagens',
    assunto: 'Interpretacao de texto',
    ano: 2023,
    dificuldade: 'media',
    enunciado:
      'No trecho "Nao basta abrir a janela / Para ver os campos e o rio.", o autor sugere que a compreensao do mundo exige:',
    alternativas: [
      { letra: 'A', texto: 'Fuga da realidade urbana', correta: false },
      { letra: 'B', texto: 'Contato sensorial passivo', correta: false },
      { letra: 'C', texto: 'Observacao ativa e reflexao', correta: true, feedback: 'Boa leitura - ver nao basta, e preciso interpretar.' },
      { letra: 'D', texto: 'Isolamento contemplativo', correta: false },
      { letra: 'E', texto: 'Rejeicao do conhecimento racional', correta: false },
    ],
    explicacao:
      'O verso contrapoe o ato fisico (abrir a janela) ao esforco interpretativo. Ver e insuficiente sem reflexao.',
  },

  // -------- NATUREZA --------
  {
    id: 'nat-01',
    subjectId: 'natureza',
    assunto: 'Genetica',
    ano: 2018,
    dificuldade: 'media',
    enunciado:
      'Um homem daltonico (X^dY) casa-se com uma mulher nao daltonica e nao portadora (X^AX^A). Qual a probabilidade de o primeiro filho do casal ser daltonico?',
    alternativas: [
      { letra: 'A', texto: '0%', correta: true, feedback: 'Correto: todos os filhos recebem X^A da mae.' },
      { letra: 'B', texto: '25%', correta: false },
      { letra: 'C', texto: '50%', correta: false },
      { letra: 'D', texto: '75%', correta: false },
      { letra: 'E', texto: '100%', correta: false },
    ],
    explicacao:
      'Como a mae e X^AX^A, nenhum filho pode herdar o alelo recessivo do daltonismo. Todas as filhas serao portadoras; nenhum filho sera daltonico.',
  },
  {
    id: 'nat-02',
    subjectId: 'natureza',
    assunto: 'Cinematica',
    ano: 2021,
    dificuldade: 'dificil',
    enunciado:
      'Um carro parte do repouso e acelera uniformemente a 2 m/s². Que distancia ele percorre em 10 segundos?',
    alternativas: [
      { letra: 'A', texto: '20 m', correta: false },
      { letra: 'B', texto: '50 m', correta: false },
      { letra: 'C', texto: '80 m', correta: false },
      { letra: 'D', texto: '100 m', correta: true, feedback: 'Exato: s = ½ · 2 · 10² = 100 m.' },
      { letra: 'E', texto: '200 m', correta: false },
    ],
    explicacao:
      'Com v₀ = 0: s = ½ a t² = ½ · 2 · 100 = 100 m.',
  },

  // -------- HUMANAS --------
  {
    id: 'hum-01',
    subjectId: 'humanas',
    assunto: 'Republica Velha',
    ano: 2019,
    dificuldade: 'media',
    enunciado:
      'A politica do "cafe com leite" durante a Republica Velha caracterizava-se pela:',
    alternativas: [
      { letra: 'A', texto: 'Alianca entre militares e industriais paulistas.', correta: false },
      { letra: 'B', texto: 'Alternancia no poder entre as oligarquias de SP e MG.', correta: true, feedback: 'Correto.' },
      { letra: 'C', texto: 'Participacao popular nas eleicoes presidenciais.', correta: false },
      { letra: 'D', texto: 'Predominancia dos coroneis do Nordeste.', correta: false },
      { letra: 'E', texto: 'Hegemonia do Partido Comunista.', correta: false },
    ],
    explicacao:
      'A politica do cafe com leite foi o arranjo de elites que garantia a alternancia na presidencia entre Sao Paulo (cafe) e Minas Gerais (leite) de 1894 a 1930.',
  },

  // -------- REDACAO --------
  {
    id: 'red-01',
    subjectId: 'redacao',
    assunto: 'Estrutura dissertativa',
    ano: 2022,
    dificuldade: 'facil',
    enunciado:
      'Qual elemento NAO e esperado em uma redacao dissertativa-argumentativa nota 1000 no ENEM?',
    alternativas: [
      { letra: 'A', texto: 'Tese clara na introducao', correta: false },
      { letra: 'B', texto: 'Argumentos com repertorio sociocultural', correta: false },
      { letra: 'C', texto: 'Proposta de intervencao com 5 elementos', correta: false },
      { letra: 'D', texto: 'Narrativa em 1ª pessoa com dialogos', correta: true, feedback: 'Certo - narrativa ficcional quebra o tipo textual.' },
      { letra: 'E', texto: 'Coesao entre paragrafos', correta: false },
    ],
    explicacao:
      'A dissertacao-argumentativa e impessoal e expositiva. Dialogos e narrativa em 1ª pessoa pertencem a tipos narrativos e prejudicam a competencia 2 (tipo textual).',
  },
];

export function getAllQuestions(): Question[] {
  return QUESTIONS;
}

/**
 * Seleciona a proxima questao para a sessao:
 *  - respeita a disciplina
 *  - evita repeticao dentro do conjunto ja visto
 *  - se build = 'sniper', filtra por dificil; se 'estrategista', facil/media
 */
export function pickQuestion(params: {
  subjectId: SubjectId;
  build?: string;
  alreadyAskedIds: string[];
}): Question | null {
  const { subjectId, build, alreadyAskedIds } = params;

  const byDifficulty = (d: Difficulty) => {
    if (build === 'sniper') return d === 'dificil';
    if (build === 'estrategista') return d !== 'dificil';
    return true;
  };

  const pool = QUESTIONS.filter(
    (q) =>
      q.subjectId === subjectId &&
      !alreadyAskedIds.includes(q.id) &&
      byDifficulty(q.dificuldade),
  );

  if (pool.length === 0) {
    // cai para qualquer nao repetida da materia
    const fallback = QUESTIONS.filter(
      (q) => q.subjectId === subjectId && !alreadyAskedIds.includes(q.id),
    );
    return fallback[0] ?? null;
  }

  // Deterministico para ser previsivel no prototipo
  return pool[0];
}
