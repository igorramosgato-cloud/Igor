# Decisões

Entradas mais recentes no topo. Formato definido em
`.claude/skills/registrar-decisao/SKILL.md`.

## 2026-09-17 — Estrutura do layout genérico de importação do Questor (CONDICIONAL)

**Contexto:** homologação física do layout de importação do Questor para o
P01 (ver `docs/P01_ART_LATEX_QUESTOR.md`).
**Decisão:** confirmada estruturalmente (por print de tela, não pelo
arquivo físico) a estrutura de um arquivo CSV (MS-DOS) de importação,
válida para qualquer cliente/evento, um arquivo por evento: linha 1/coluna
D = código do evento; linha 2/coluna D = tipo (`V`=Valor observado; `H`
seria o equivalente para Hora); linha 3 = cabeçalho `CÓDIGO`/`NOME`; linha
4+ = dados por funcionário. Classificação: **CONDICIONAL** — delimitador,
encoding e precisão decimal real ainda não confirmados, pois só um print
foi recebido, não o arquivo físico. Nenhum dado do print (nomes, valores,
códigos de funcionário) foi reproduzido em qualquer arquivo do repositório.
**Evidência:** print de tela fornecido pelo usuário em 2026-09-17,
descrito como arquivo já aceito/importado com sucesso no Questor.
**Impacto:** `docs/P01_ART_LATEX_QUESTOR.md` (seção "Layout do importador
do Questor — achados"). Nenhuma mudança em `config/clientes/art_latex.json`
ou `src/jrdp/serializers.py` — a divergência observada na precisão decimal
dos valores não deve ser incorporada ao código sem o arquivo físico.

## 2026-09-16 — Regras de eventos ART LATEX (Filial e Matriz)

**Contexto:** definição dos códigos de evento usados na importação de
variáveis/benefícios do ART LATEX para o Questor.
**Decisão:** códigos confirmados conforme `config/clientes/art_latex.json`
(Filial: 35, 49, 23, 29, 25, 1955, 815, 1524, 806, 813, 96; Matriz: 50). O
código da Cesta Básica da Matriz (coluna E "Desconto") fica PENDENTE — sem
evidência suficiente para definição.
**Evidência:** consolidação fornecida pelo usuário na sessão de estruturação
do projeto.
**Impacto:** `config/clientes/art_latex.json`, `.claude/rules/art-latex.md`.

## 2026-09-16 — Formato de hora H,MM travado por teste

**Contexto:** risco de uma futura alteração de código transformar a regra
do importador (H,MM) em hora decimal matemática.
**Decisão:** `01:30` deve sempre serializar para `1,30`, nunca `1,50`.
**Evidência:** confirmação explícita do usuário com exemplos (00:32→0,32,
01:52→1,52, 04:07→4,07, 06:00→6,00).
**Impacto:** `src/jrdp/serializers.py`,
`tests/test_serializers.py::test_hmm_never_converts_to_decimal_hours`.

## Erros históricos

### Evento 1603 (07/2026) — ART LATEX

Foi um erro histórico e não deve ser reaproveitado como referência de
código de evento em nenhuma automação futura. Bloqueado em
`config/clientes/art_latex.json` (`erros_historicos`) e coberto por
`tests/test_art_latex.py::test_bloqueia_evento_1603_como_erro_historico`.
