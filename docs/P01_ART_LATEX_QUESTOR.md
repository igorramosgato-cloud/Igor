# P01 — Variáveis + Benefícios ART LATEX → Questor

## Status: BLOCKED para geração de produção

Regras de negócio já parametrizadas (`config/clientes/art_latex.json`,
`.claude/rules/art-latex.md`) e cobertas por testes (`tests/test_art_latex.py`,
`tests/test_config.py`, `tests/test_serializers.py`).

## Layout do importador do Questor — achados (2026-09-17)

Evidência recebida: print de tela de um arquivo CSV (MS-DOS) descrito pelo
usuário como já aceito/importado com sucesso pelo Questor. O layout é
genérico (usado para qualquer cliente, inclusive ART LATEX), um arquivo por
evento. Nenhum dado do print (nomes, valores, códigos de funcionário) foi
reproduzido em nenhum arquivo do repositório — ver
`.claude/rules/homologacao-dados.md`.

### CONFIRMADO POR EVIDÊNCIA FÍSICA (estrutural)

- Linha 1, coluna D: código do evento (ex.: no print, 1889).
- Linha 2, coluna D: tipo do evento (`V` = Valor observado no print; `H`
  para Hora seria o equivalente por extensão, não observado diretamente).
- Linha 3: cabeçalho — coluna A = `CÓDIGO`, coluna B = `NOME`.
- Linha 4 em diante: coluna A = código do funcionário, coluna B = nome,
  coluna D = valor/hora do evento.
- Coluna C aparenta ficar em branco.
- Formato de arquivo: CSV (MS-DOS), um arquivo por evento.

### CONDICIONAL (precisa do arquivo físico, não apenas do print, para confirmar)

- Delimitador exato usado no arquivo (print não revela; CSV MS-DOS do Excel
  normalmente usa `;` em locale pt-BR, mas isso não foi confirmado).
- Encoding exato (CSV "MS-DOS" no Excel tipicamente grava em codepage OEM,
  ex. CP850 — relevante para nomes com acento; não confirmado no print).
- Precisão decimal real dos valores. O print mostra, na coluna D, valores
  com 1 a 5 casas decimais no mesmo arquivo (formato de exibição "Geral" no
  Excel) — isso diverge da regra atual de `serializers.serialize_valor`
  (sempre 2 casas). Não alterar essa regra sem o arquivo físico: o Excel
  pode estar exibindo artefato de arredondamento que não existe no CSV.
- Se o par (linha 1 = código, linha 2 = tipo) se repete por coluna quando
  há múltiplos eventos no mesmo arquivo (ex.: coluna E, F...) ou se cada
  evento sempre gera um arquivo separado.
- Chave de identificação do funcionário: o print mostra "CÓDIGO", mas não
  confirma se esse código bate com a chave usada em outros sistemas
  (Sankhya, ponto) — ver `.claude/rules/matching.md`.

### PENDENTE (sem evidência ainda)

- Código do evento da Cesta Básica da Matriz (ver `.claude/rules/art-latex.md`).
- Versão específica do Questor/layout do conversor.

## Pendências para liberar a geração real

1. ~~Layout real/versionado do importador do Questor~~ — parcialmente
   confirmado por print (ver seção acima); falta o **arquivo físico** para
   confirmar delimitador, encoding e precisão decimal.
2. Planilhas-fonte reais Matriz/Filial (abas e cabeçalhos).
3. Chave usada para identificar o funcionário (confirmar se "CÓDIGO" do
   layout Questor bate com a chave das planilhas de origem).
4. Código do evento da Cesta Básica da Matriz.
5. Versão específica do Questor/layout do conversor.
6. Exemplo de **arquivo físico** (não print) que efetivamente importou com
   sucesso, para testes de contrato do layout.

Ver `.claude/skills/gerar-questor/SKILL.md` para o procedimento completo e
`docs/BACKLOG.md` para o próximo passo.
