import type { SubjectId } from './types';

/** IDs da tabela Habilidade no Supabase: 1=Linguagens 2=Humanas 3=Matemática 4=Natureza */
export const SUBJECT_HABILIDADE_ID: Record<SubjectId, number> = {
  linguagens: 1,
  humanas: 2,
  matematica: 3,
  natureza: 4,
  redacao: 5,
};

const HABILIDADE_NOME: Record<number, string> = {
  1: 'Linguagens',
  2: 'Ciências Humanas',
  3: 'Matemática',
  4: 'Ciências da Natureza',
  5: 'Redação'
};

export function subjectToHabilidadeId(subjectId: SubjectId): number {
  return SUBJECT_HABILIDADE_ID[subjectId];
}

export function habilidadeNome(habilidadeId: number): string {
  return HABILIDADE_NOME[habilidadeId] ?? `Área ${habilidadeId}`;
}
