import { findBuild, findSubject } from '../catalog';
import { pickQuestion } from '../questionBank';
import type {
  AnswerInput,
  AnswerOutput,
  CommandActionInput,
  CommandActionOutput,
  FreeReplyInput,
  FreeReplyOutput,
  HighlightInput,
  HighlightOutput,
  LlmClient,
  NextQuestionInput,
  NextQuestionOutput,
  ReviewItem,
  ReviewQueueInput,
  ReviewQueueOutput,
  SessionInsightsInput,
  SessionInsightsOutput,
  SmartSuggestion,
  StartSessionInput,
  StartSessionOutput,
  StudyPlanInput,
  StudyPlanOutput,
} from './llmClient';
import type { SubjectId } from '../types';

/* =========================================================================
   MOCK client — retornos plausiveis com markdown, callouts, formulas e IA fake.
   Trocar por implementacao real (OpenAI, etc.) criando outro arquivo que
   implemente LlmClient e alterando o export em ./index.ts.
   ========================================================================= */

function delay(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}
function pickOne<T>(arr: readonly T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}
function sid(prefix = 's') {
  return `${prefix}_${Math.random().toString(36).slice(2, 9)}`;
}

/* ---------- Greetings & flavor ---------- */

const GREETINGS: Record<string, string[]> = {
  estrategista: [
    'Modo **Estrategista** ativado. Cada questão tem cronômetro de 2 minutos. Vamos marcar ritmo.',
    'Estrategista no ar. A meta é `tempo por questão < 2min`. Bora afiar.',
  ],
  teorico: [
    'Modo **Teórico**. A gente vai com calma — entender > acertar no chute.',
    'Modo Teórico ativo. A cada questão eu destaco o conceito-chave **antes** e explico com calma no fim.',
  ],
  sniper: [
    'Modo **Sniper** — só questões de alto nível cairão aqui. Errar aqui é onde se aprende.',
    'Sniper travado nas difíceis. Mira firme.',
  ],
};

function subjectGreeting(subjectId: SubjectId): string {
  const subject = findSubject(subjectId);
  const hook: Record<SubjectId, string> = {
    matematica: 'No ENEM, 70% das questões de matemática são de interpretação. Desenhar o problema é seu atalho.',
    linguagens: 'Ler alternativas **antes** do enunciado costuma acelerar 30% o tempo. Teste.',
    natureza: 'ENEM ama contexto: meio ambiente, saúde e tecnologia. Sempre conecte conceito a cenário.',
    humanas: 'Cronologia importa. Causa → consequência é a lente mental para quase toda questão.',
    redacao: 'Repertório precisa ser **legítimo e pertinente**: dados, leis, obras. Decorar frase solta não cola.',
  };
  return `Oi, sou seu tutor de **${subject?.title ?? 'ENEM'}**. ${hook[subjectId]}`;
}

function buildCallout(text: string): string {
  return `\n\n<callout>${text}</callout>\n\n`;
}

/* ---------- Smart suggestions factory ---------- */

function suggestionsAfterWrong(): SmartSuggestion[] {
  return [
    { id: sid(), action: 'easier', label: 'Quero uma mais fácil', icon: '🪶' },
    { id: sid(), action: 'summary', label: 'Resumo do tópico', icon: '📝' },
    { id: sid(), action: 'similar', label: 'Questão parecida', icon: '🔁' },
    { id: sid(), action: 'explain-simple', label: 'Explique como se eu tivesse 10 anos', icon: '🧒' },
  ];
}

function suggestionsAfterCorrect(): SmartSuggestion[] {
  return [
    { id: sid(), action: 'harder', label: 'Aumenta a dificuldade', icon: '🔥' },
    { id: sid(), action: 'similar', label: 'Outra do mesmo tipo', icon: '🔁' },
    { id: sid(), action: 'next', label: 'Próxima questão', icon: '→' },
    { id: sid(), action: 'flashcards', label: 'Criar flashcards desse tópico', icon: '🗂️' },
  ];
}

/* ---------- Mock client ---------- */

export const mockLlmClient: LlmClient = {
  async startSession({ subjectId, build }): Promise<StartSessionOutput> {
    await delay(380);
    const buildMeta = build ? findBuild(build) : undefined;

    const firstQuestion = pickQuestion({ subjectId, build, alreadyAskedIds: [] });
    if (!firstQuestion) {
      throw new Error(`Nao ha questoes mockadas para a disciplina ${subjectId}`);
    }

    const greeting = [
      subjectGreeting(subjectId),
      buildMeta ? pickOne(GREETINGS[buildMeta.id] ?? []) : '',
      buildMeta?.systemPitch ?? '',
      '',
      'Quando estiver pronto, escolha uma alternativa abaixo — ou digite `/` para ver os atalhos.',
    ]
      .filter(Boolean)
      .join('\n\n');

    return { greeting, firstQuestion };
  },

  async answerQuestion({ question, chosen, build }: AnswerInput): Promise<AnswerOutput> {
    await delay(520);
    const alt = question.alternativas.find((a) => a.letra === chosen);
    const correta = Boolean(alt?.correta);
    const correctLetter = question.alternativas.find((a) => a.correta)?.letra ?? '?';

    if (correta) {
      const body =
        [
          `**Correto.** Resposta ${chosen} é a certa.`,
          alt?.feedback ? `\n> ${alt.feedback}` : '',
          build === 'teorico' ? `\n\n**Por quê funciona:** ${question.explicacao}` : '',
          build === 'estrategista' ? buildCallout('⏱ Boa — marque o tempo que levou e tente bater na próxima.') : '',
        ]
          .filter(Boolean)
          .join('\n');
      return {
        correta: true,
        feedback: body,
        explicacao: question.explicacao,
        suggestions: suggestionsAfterCorrect(),
      };
    }

    const body = [
      `**Não foi dessa vez.** A resposta correta era **${correctLetter}**.`,
      alt?.feedback ? `\n> ${alt.feedback}` : '',
      `\n**Raciocínio:** ${question.explicacao}`,
      build === 'teorico' ? buildCallout('💡 Releia o enunciado marcando os números/palavras-chave antes de olhar as alternativas.') : '',
    ]
      .filter(Boolean)
      .join('\n');
    return {
      correta: false,
      feedback: body,
      explicacao: question.explicacao,
      suggestions: suggestionsAfterWrong(),
    };
  },

  async nextQuestion({ subjectId, build, alreadyAskedIds, adaptiveHint }: NextQuestionInput): Promise<NextQuestionOutput> {
    await delay(300);
    const effectiveBuild = adaptiveHint === 'facil' ? 'estrategista' : adaptiveHint === 'dificil' ? 'sniper' : build;
    const q = pickQuestion({ subjectId, build: effectiveBuild, alreadyAskedIds });
    if (!q) {
      return {
        intro:
          'Você já respondeu todas as questões disponíveis desta matéria no protótipo. Quando a IA estiver plugada, vou gerar novas na hora.',
        question: null,
      };
    }
    const intros = [
      'Próxima — leia com calma.',
      'Bora pra próxima:',
      'Mais uma, vamos:',
      'Próximo desafio:',
    ];
    return { intro: pickOne(intros), question: q };
  },

  async freeReply({ userMessage, subjectId, build, lastQuestion }: FreeReplyInput): Promise<FreeReplyOutput> {
    await delay(420);
    const lower = userMessage.toLowerCase().trim();
    const buildMeta = build ? findBuild(build) : undefined;

    if (/(dica|hint|ajuda|como resolver|nao entendi)/.test(lower) && lastQuestion) {
      return {
        reply: [
          `**Dica rápida** para esta questão:`,
          ``,
          `- Identifique o que está sendo perguntado antes de olhar as alternativas.`,
          `- Grife os dados numéricos ou palavras-chave.`,
          `- Se tiver fórmula, escreva antes de substituir valores.`,
          ``,
          `> ${lastQuestion.explicacao.split('.')[0]}.`,
          ``,
          `Quer que eu **explique** com mais detalhes? Seleciona um trecho da questão ou diga "explicar".`,
        ].join('\n'),
      };
    }

    if (/(explique|explica|aprofund|detalh)/.test(lower) && lastQuestion) {
      return {
        reply: `**Explicação completa:**\n\n${lastQuestion.explicacao}\n\n${buildCallout(
          'Se quiser treinar isso, peça uma **questão parecida** ou crie **flashcards** pelo Cmd+K.',
        )}`,
      };
    }

    if (/(parar|pausa|depois|sair)/.test(lower)) {
      return { reply: 'Sem problema. Seu progresso fica salvo. Volte quando quiser — sugiro **revisar hoje os tópicos fracos** no painel da direita.' };
    }

    if (/(oi|ola|hello|e ai)/.test(lower)) {
      return { reply: 'Oi! Tô aqui para te ajudar. Quer continuar de onde paramos? Digite `/` para ver atalhos ou aperte `Cmd+K` para a paleta de comandos.' };
    }

    return {
      reply: [
        `Entendi. Em **${findSubject(subjectId)?.title ?? 'ENEM'}**${buildMeta ? ` (modo ${buildMeta.title})` : ''}, algumas coisas que posso fazer:`,
        ``,
        `- \`/proxima\` — me envie uma nova questão`,
        `- \`/dica\` — dica para a questão atual`,
        `- \`/simplificar\` — explicação para iniciante`,
        `- \`/flashcards\` — gerar cartões de revisão`,
        ``,
        `Ou diga o que está te travando.`,
      ].join('\n'),
    };
  },

  async highlight({ selectedText, action }: HighlightInput): Promise<HighlightOutput> {
    await delay(480);
    const snippet = selectedText.length > 100 ? selectedText.slice(0, 100) + '…' : selectedText;
    if (action === 'explicar') {
      return {
        title: 'Explicação',
        body: `> "${snippet}"\n\nEssa passagem está dizendo, em outras palavras, que o conceito-chave envolve estabelecer relação causa → consequência. No ENEM, isso aparece muito como armadilha: a alternativa certa **não** é a que repete o texto, é a que **sintetiza** a relação.`,
      };
    }
    if (action === 'aprofundar') {
      return {
        title: 'Aprofundando',
        body: `**Sobre "${snippet}"**\n\nNo currículo ENEM, esse ponto se conecta a três ideias maiores:\n\n1. **Contexto histórico/científico** — qual o pano de fundo.\n2. **Aplicação prática** — onde isso aparece no mundo real.\n3. **Pegadinhas comuns** — confusões mais frequentes.\n\nSe quiser, posso gerar uma questão sobre esse ponto.`,
      };
    }
    if (action === 'gerar-questao') {
      return {
        title: 'Questão gerada',
        body: `Criei uma questão baseada em:\n\n> ${snippet}\n\n*(No protótipo ainda não insiro a questão no chat automaticamente — com a IA real, essa ação empurra direto pro stream.)*`,
      };
    }
    return {
      title: 'Traduzindo',
      body: `"${snippet}" em linguagem simples: ${snippet.toLowerCase().includes('quando') ? 'é uma condição que precisa acontecer antes.' : 'é o núcleo da ideia — o resto do texto gira em torno disso.'}`,
    };
  },

  async buildStudyPlan({ goal, minutesPerDay = 60, days = 7 }: StudyPlanInput): Promise<StudyPlanOutput> {
    await delay(680);
    const lower = goal.toLowerCase();
    const focoExatas = /(exata|matemat|fisic|quimic)/.test(lower);
    const focoHumanas = /(humana|historia|geograf|sociolog|filosof)/.test(lower);
    const focoRedacao = /(redac|escrev|texto)/.test(lower);

    const labelDays = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
    const base: Array<{ subject: SubjectId; topic: string }> = focoExatas
      ? [
          { subject: 'matematica', topic: 'Funções e proporcionalidade' },
          { subject: 'natureza', topic: 'Cinemática (MRU + MRUV)' },
          { subject: 'matematica', topic: 'Estatística e probabilidade' },
          { subject: 'natureza', topic: 'Estequiometria' },
          { subject: 'matematica', topic: 'Geometria plana' },
          { subject: 'natureza', topic: 'Genética mendeliana' },
          { subject: 'redacao', topic: 'Prática de redação — tema livre' },
        ]
      : focoHumanas
        ? [
            { subject: 'humanas', topic: 'República Velha e Era Vargas' },
            { subject: 'humanas', topic: 'Globalização e blocos econômicos' },
            { subject: 'linguagens', topic: 'Interpretação de texto' },
            { subject: 'humanas', topic: 'Filosofia antiga e clássica' },
            { subject: 'humanas', topic: 'Cartografia e geopolítica' },
            { subject: 'linguagens', topic: 'Variação linguística' },
            { subject: 'redacao', topic: 'Prática de redação' },
          ]
        : focoRedacao
          ? [
              { subject: 'redacao', topic: 'Estrutura dissertativa-argumentativa' },
              { subject: 'redacao', topic: 'Repertório: direitos humanos' },
              { subject: 'redacao', topic: 'Proposta de intervenção' },
              { subject: 'redacao', topic: 'Coesão e coerência' },
              { subject: 'linguagens', topic: 'Figuras de linguagem e sentido' },
              { subject: 'redacao', topic: 'Simulado de redação cronometrado' },
              { subject: 'redacao', topic: 'Revisão e reescrita da semana' },
            ]
          : [
              { subject: 'matematica', topic: 'Funções e gráficos' },
              { subject: 'linguagens', topic: 'Interpretação e literatura' },
              { subject: 'natureza', topic: 'Física — mecânica aplicada' },
              { subject: 'humanas', topic: 'Brasil República' },
              { subject: 'matematica', topic: 'Geometria e áreas' },
              { subject: 'natureza', topic: 'Biologia — genética' },
              { subject: 'redacao', topic: 'Redação cronometrada' },
            ];

    const week = Array.from({ length: Math.min(days, 7) }).map((_, i) => ({
      day: labelDays[i % 7],
      subjectId: base[i].subject,
      topic: base[i].topic,
      minutes: minutesPerDay,
      goal: i === 6 ? 'Revisar + escrever texto' : i === 5 ? 'Aumentar dificuldade' : 'Fixar base',
    }));

    return {
      title: `Plano semanal · ${minutesPerDay} min/dia`,
      overview:
        `Plano gerado com foco em: _${goal || 'equilibrio geral'}_. Mistura blocos de aprendizado novo com revisão espacada.` +
        ` No **domingo** fechamos com redação ou simulado para consolidar a semana.`,
      week,
    };
  },

  async sessionInsights({ stats, subjectId }: SessionInsightsInput): Promise<SessionInsightsOutput> {
    await delay(180);
    const accuracy = stats.answered > 0 ? Math.round((stats.correct / stats.answered) * 100) : 0;
    const streak = stats.streak ?? Math.min(stats.correct, 3);
    const mockStrong =
      subjectId === 'matematica'
        ? [{ topic: 'Probabilidade', accuracy: 100 }, { topic: 'Funções', accuracy: 85 }]
        : subjectId === 'linguagens'
          ? [{ topic: 'Figuras de linguagem', accuracy: 100 }, { topic: 'Interpretação', accuracy: 78 }]
          : [{ topic: 'Base conceitual', accuracy: 80 }];
    const mockWeak =
      subjectId === 'matematica'
        ? [{ topic: 'Geometria espacial', accuracy: 40 }]
        : subjectId === 'natureza'
          ? [{ topic: 'Cinemática', accuracy: 33 }]
          : [{ topic: 'Análise argumentativa', accuracy: 45 }];

    return {
      accuracy,
      streak,
      timeMinutes: Math.max(4, Math.round(stats.answered * 1.5)),
      strongTopics: mockStrong,
      weakTopics: mockWeak,
      nextAction:
        accuracy >= 70
          ? { type: 'challenge', label: 'Subir dificuldade', detail: 'Você está acertando bastante — hora de testar questões difíceis.' }
          : accuracy >= 40
            ? { type: 'review', label: 'Revisar ponto fraco', detail: `Concentre em ${mockWeak[0].topic} antes de seguir.` }
            : { type: 'new-topic', label: 'Mudar a abordagem', detail: 'Tente o modo Teórico — você vai ganhar contexto antes de responder.' },
    };
  },

  async reviewQueue({ subjectId }: ReviewQueueInput): Promise<ReviewQueueOutput> {
    await delay(160);
    const focus = subjectId ?? 'matematica';
    const today: ReviewItem[] = [
      { id: sid('r'), subjectId: focus, topic: 'Regra de três composta', dueLabel: 'Hoje', overdue: false, interval: '3 dias' },
      { id: sid('r'), subjectId: 'linguagens', topic: 'Metáfora vs metonímia', dueLabel: 'Hoje', overdue: false, interval: '1 dia' },
      { id: sid('r'), subjectId: 'natureza', topic: 'Estequiometria — mol', dueLabel: 'Hoje', overdue: true, interval: '7 dias' },
    ];
    const upcoming: ReviewItem[] = [
      { id: sid('r'), subjectId: 'humanas', topic: 'Guerra Fria', dueLabel: 'Amanhã', overdue: false, interval: '5 dias' },
      { id: sid('r'), subjectId: 'redacao', topic: 'Proposta de intervenção', dueLabel: 'em 2 dias', overdue: false, interval: '7 dias' },
    ];
    return {
      dueToday: today,
      upcoming,
      summary: `Você tem **${today.length} itens** para revisar hoje. Revisar no prazo mantém retenção acima de 80%.`,
    };
  },

  async runCommand({ actionId, context }: CommandActionInput): Promise<CommandActionOutput> {
    await delay(260);
    switch (actionId) {
      case 'generate-similar':
        return {
          reply: [
            '**Gerando questão similar…**',
            '',
            'Quando a IA real estiver plugada, aqui eu monto uma questão nova com:',
            '- mesmo tópico e habilidade ENEM',
            '- dificuldade próxima (± 1 nível)',
            '- enunciado reescrito',
            '',
            '_Protótipo: uso o banco de questões do mesmo assunto no fluxo `/proxima`._',
          ].join('\n'),
        };
      case 'explain-eli5':
        return {
          reply:
            context?.question
              ? [
                  '**Explicando como se você tivesse 10 anos:**',
                  '',
                  `Imagina que ${context.question.assunto.toLowerCase()} é tipo um jogo com regras. A regra mais importante dessa questão é simples: `,
                  '',
                  `> ${context.question.explicacao.split('.')[0]}.`,
                  '',
                  'Se você se lembrar só disso, acerta 80% das vezes.',
                ].join('\n')
              : 'Sem questão no contexto — gere uma primeiro que eu explico.',
        };
      case 'summarize-topic':
        return {
          reply: [
            `**Resumo rápido — ${context?.question?.assunto ?? 'Tópico'}**`,
            '',
            '- **Ideia-chave:** o conceito central é X.',
            '- **Quando cai no ENEM:** costuma aparecer junto com interpretação de gráficos/texto.',
            '- **Armadilha típica:** confundir correlação com causa.',
            '- **Fórmula/regra essencial:** ',
            '',
            '```',
            'resultado = f(entrada) sob condição C',
            '```',
            '',
            '> Peça flashcards pelo `Cmd+K` se quiser fixar.',
          ].join('\n'),
        };
      case 'flashcards':
        return { openModal: 'flashcards' };
      case 'quiz-topic':
        return {
          reply:
            '**Mini-quiz sobre este tópico** — vou enviar 3 questões seguidas focadas neste conteúdo. Digite `/proxima` para começar.',
        };
      case 'simulate-exam':
        return { openModal: 'exam-sim' };
      case 'open-study-plan':
        return { openModal: 'study-plan' };
      case 'toggle-theme':
        return { sideEffect: { type: 'theme', value: 'dark' } };
      case 'next-question':
        return { reply: '__next__' };
      case 'give-hint':
        return {
          reply:
            context?.question
              ? [
                  '**Dica sem entregar a resposta:**',
                  '',
                  `Foca em identificar **o que está sendo pedido**. Em "${context.question.assunto}" o erro mais comum é ler a alternativa antes do enunciado.`,
                ].join('\n')
              : 'Sem questão ativa.',
        };
      case 'switch-build':
        return {
          sideEffect: { type: 'build', value: context?.build ?? 'teorico' },
        };
      case 'start-focus-timer':
        return { reply: '⏱ **Foco iniciado:** 25 minutos. Vou pausar as sugestões até o timer zerar. *(simulação)*' };
      default:
        return { reply: 'Ação não reconhecida.' };
    }
  },
};
