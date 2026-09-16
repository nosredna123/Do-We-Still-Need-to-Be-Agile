export const themes = [
  {
    id: "1",
    name: "Orçamento Pessoal",
    description: "Controle de gastos e planejamento financeiro",
    progress: 70,
    cards: [
      { id: "c1", question: "Qual a definição de renda?", answer: "Renda é todo o dinheiro que entra no seu orçamento, como salário, bônus ou rendimentos de investimentos." },
      { id: "c2", question: "Qual a diferença entre renda bruta e renda líquida?", answer: "Renda bruta é o valor total recebido, enquanto renda líquida é o que sobra após os descontos de impostos e benefícios." },
      { id: "c3", question: "O que são despesas fixas?", answer: "São gastos que ocorrem todo mês com valores semelhantes, como aluguel, condomínio e mensalidade escolar." },
      { id: "c4", question: "Cite 3 exemplos de despesas variáveis.", answer: "Alimentação (restaurantes), lazer, vestuário e contas de consumo que variam como energia e água." },
    ]
  },
  {
    id: "2",
    name: "Investimentos",
    description: "Como fazer seu dinheiro render com segurança",
    progress: 25,
    cards: [
      { id: "c5", question: "O que é Selic?", answer: "É a taxa básica de juros da economia brasileira, que influencia todas as outras taxas." },
      { id: "c6", question: "O que significa diversificação?", answer: "É a estratégia de distribuir seus recursos em diferentes tipos de ativos para reduzir riscos." },
    ]
  },
  {
    id: "3",
    name: "Impostos",
    description: "Declaração de IR e restituições federais",
    progress: 40,
    cards: [
      { id: "c7", question: "O que é o IRPF?", answer: "Imposto sobre a Renda das Pessoas Físicas, um tributo federal sobre os ganhos anuais." },
      { id: "c8", question: "O que é malha fina?", answer: "É o processo de retenção da declaração para conferência de inconsistências pela Receita Federal." },
    ]
  }
];

export const weeks = [
  {
    id: 1,
    title: "Semana 1: Fundamentos",
    days: [
      { name: "Segunda", topics: ["Introdução a Finanças"] },
      { name: "Terça", topics: ["Renda e Despesas"] },
      { name: "Quarta", topics: ["Fluxo de Caixa"] },
      { name: "Quinta", topics: ["Planejamento"] },
      { name: "Sexta", topics: ["Revisão"] },
    ]
  },
  { id: 2, title: "Semana 2: Investimentos", days: [] },
  { id: 3, title: "Semana 3: Impostos", days: [] },
  { id: 4, title: "Semana 4: Consolidação", days: [] },
];
