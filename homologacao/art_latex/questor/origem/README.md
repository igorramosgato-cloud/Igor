# origem/

Coloque aqui as planilhas reais de origem da ART LATEX (Matriz, Filial,
Benefícios, Ponto/variáveis quando aplicável).

**Estes arquivos NUNCA são versionados no Git** — ver
`.claude/rules/homologacao-dados.md`. Eles ficam só localmente. O que entra
no repositório é o registro em `../evidencia/manifest.json` (nome, SHA-256,
competência, status) e o contexto em `../evidencia/README.md`.

## Recebido até agora

- **2026-09-17**: `planilha_importacao_matriz.xlsm` e
  `planilha_importacao_filial.xlsm` (arquivos reais, macro-habilitados).
  Inventariados estruturalmente — achados completos em
  `docs/P01_ART_LATEX_QUESTOR.md`. Revelaram um bloqueio de matching
  (coluna de código do funcionário vazia em todos os registros reais) e
  duas divergências registradas em `docs/DECISIONS.md`. Contêm dados
  pessoais reais, incluindo CPF na aba "Plano de saúde" da Filial —
  nunca abrir/copiar esses arquivos para fora desta pasta local.
