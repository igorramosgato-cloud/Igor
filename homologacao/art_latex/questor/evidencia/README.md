# Evidência — Homologação layout Questor (ART LATEX)

Esta pasta recebe a evidência física necessária para tirar o P01 do estado
`BLOCKED` de geração de produção. Ver `docs/P01_ART_LATEX_QUESTOR.md` e
`.claude/skills/gerar-questor/SKILL.md`.

## O que colocar aqui

- `layout_aceito/` — arquivo/modelo que o Questor **já aceitou/importou com
  sucesso** (a evidência primária de layout). Preferencialmente com o nome
  original, mais uma cópia renomeada indicando a data e se é produção ou
  homologação.
- `origem/` — planilhas reais de origem da ART LATEX (Matriz, Filial,
  Benefícios, Ponto/variáveis quando aplicável).
- `evidencia/` (esta pasta) — anotações sobre a origem de cada arquivo:
  quem forneceu, quando, se é dado real de produção ou exemplo, e qualquer
  contexto necessário para registrar em `docs/SOURCE_REGISTRY.md`.

## Regra

Nenhum arquivo colocado aqui é usado para gerar produção diretamente. Ele é
inventariado, comparado com `config/clientes/art_latex.json` e as regras em
`.claude/rules/art-latex.md`, e qualquer divergência é registrada como
conflito — nunca sobrescrita silenciosamente (ver `.claude/rules/governanca.md`).

## Registro de arquivos recebidos

| Arquivo | Origem | Data de coleta | Produção ou exemplo | Fornecido por |
|---|---|---|---|---|
| _(nenhum arquivo recebido ainda)_ | | | | |
