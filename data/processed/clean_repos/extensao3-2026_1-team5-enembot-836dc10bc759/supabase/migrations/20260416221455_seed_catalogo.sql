-- Seed de catalogo minimo para o prototipo funcionar end-to-end.

insert into public.instituicao (nome, sigla, status, uf) values
  ('Universidade Federal do Ceara', 'UFC', true, 'CE'),
  ('Universidade Estadual do Ceara', 'UECE', true, 'CE')
on conflict do nothing;

insert into public.banca (nome, sigla) values
  ('INEP', 'INEP')
on conflict (nome) do nothing;

insert into public.disciplina (nome, cor_hex, icone) values
  ('Matematica',           '#1ec3a6', '📐'),
  ('Linguagens',            '#5f8bff', '📖'),
  ('Ciencias da Natureza',  '#9553f3', '🧪'),
  ('Ciencias Humanas',      '#f59b22', '🌍'),
  ('Redacao',               '#f04383', '✍️')
on conflict (nome) do nothing;

insert into public.tags (nome, descricao, cor_hex, icone) values
  ('Revisao Critica',  'Temas que voce tem dificuldade, revise com prioridade.', '#dc3545', 'bi-exclamation-triangle-fill'),
  ('Alto Rendimento',  'Questoes que exigem raciocinio aprofundado.',             '#0d6efd', 'bi-gem'),
  ('Pegadinha Classica','Alternativas distratoras comuns em provas do ENEM.',      '#ffc107', 'bi-lightbulb-fill'),
  ('Conceito-Chave',   'Conceito fundamental para o ENEM.',                        '#198754', 'bi-key-fill'),
  ('Favorita',         'Salve para consultar ou estudar depois.',                 '#6c757d', 'bi-star-fill')
on conflict (nome) do nothing;

-- Assuntos por disciplina (simplificado para prototipo)
insert into public.assunto (nome, id_disciplina)
select s.nome, d.id_disciplina
from (values
  ('Matematica',           'Funcoes e graficos'),
  ('Matematica',           'Geometria plana'),
  ('Matematica',           'Probabilidade e estatistica'),
  ('Linguagens',            'Interpretacao de texto'),
  ('Linguagens',            'Figuras de linguagem'),
  ('Ciencias da Natureza',  'Genetica'),
  ('Ciencias da Natureza',  'Cinematica'),
  ('Ciencias Humanas',      'Republica Velha'),
  ('Ciencias Humanas',      'Globalizacao'),
  ('Redacao',               'Estrutura dissertativa-argumentativa')
) as s(disciplina, nome)
join public.disciplina d on d.nome = s.disciplina
on conflict do nothing;
