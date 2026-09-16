# Evidência — Homologação layout Questor (ART LATEX)

Esta pasta recebe a evidência necessária para tirar o P01 do estado
`BLOCKED` de geração de produção. Ver `docs/P01_ART_LATEX_QUESTOR.md`,
`.claude/skills/gerar-questor/SKILL.md` e, principalmente,
`.claude/rules/homologacao-dados.md`.

## Política de dados

Os arquivos físicos reais (xlsx/pdf com dados de colaboradores) **não são
versionados**. Eles ficam localmente em `../layout_aceito/` e `../origem/`.
O que é versionado aqui é:

- `manifest.json` — um registro por arquivo recebido, com hash SHA-256 (não
  o conteúdo), para rastreabilidade e reprodutibilidade sem exposição de
  dado pessoal;
- este `README.md` — contexto textual sem dados pessoais.

## Formato de uma entrada em `manifest.json`

```json
{
  "arquivo": "modelo_questor.xlsx",
  "pasta": "layout_aceito",
  "sha256": "<hash sha256 do arquivo>",
  "competencia": "08/2026",
  "cliente": "ART LATEX",
  "status": "CONFIRMADO",
  "observacao": "Arquivo informado como importado com sucesso no Questor",
  "recebido_em": "2026-09-16",
  "fornecido_por": "<quem forneceu>"
}
```

`status` segue a mesma classificação usada na homologação do P01:
`CONFIRMADO_POR_EVIDENCIA_FISICA`, `CONDICIONAL`, `PENDENTE`, `HISTORICO` ou
`DESCARTADO`.

## Como calcular o SHA-256 de um arquivo (para preencher o manifest)

```bash
sha256sum caminho/para/o/arquivo.xlsx
```

## Regra

Nenhum arquivo local aqui é usado para gerar produção diretamente. Ele é
inventariado, comparado com `config/clientes/art_latex.json` e as regras em
`.claude/rules/art-latex.md`, e qualquer divergência é registrada como
conflito — nunca sobrescrita silenciosamente (ver `.claude/rules/governanca.md`).
