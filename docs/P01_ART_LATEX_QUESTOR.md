# P01 — Variáveis + Benefícios ART LATEX → Questor

## Status: BLOCKED para geração de produção

Regras de negócio já parametrizadas (`config/clientes/art_latex.json`,
`.claude/rules/art-latex.md`) e cobertas por testes (`tests/test_art_latex.py`,
`tests/test_config.py`, `tests/test_serializers.py`).

## Pendências para liberar a geração real

1. Layout real/versionado do importador do Questor.
2. Planilhas-fonte reais Matriz/Filial (abas e cabeçalhos).
3. Chave usada para identificar o funcionário.
4. Código do evento da Cesta Básica da Matriz.
5. Versão específica do Questor/layout do conversor.
6. Exemplo de arquivo que efetivamente importou com sucesso.

Ver `.claude/skills/gerar-questor/SKILL.md` para o procedimento completo e
`docs/BACKLOG.md` para o próximo passo.
