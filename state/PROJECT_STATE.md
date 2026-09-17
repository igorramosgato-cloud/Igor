# Estado do projeto

**Atualizado em:** 2026-09-17

## Onde estamos

Roadmap item 1 (Variáveis + Benefícios → Questor, cliente ART LATEX) em
andamento. Regras de negócio parametrizadas e testadas (26/26 testes
passando). Geração de arquivo de produção continua `BLOCKED`.

Avanço em 2026-09-17: recebido um **print** (não o arquivo físico) do
layout genérico de importação do Questor, confirmando estruturalmente
(CONDICIONAL) linha do código do evento, linha do tipo (H/V), cabeçalho
CÓDIGO/NOME e disposição das colunas. Ainda falta o arquivo físico para
confirmar delimitador, encoding e precisão decimal real — ver
`docs/P01_ART_LATEX_QUESTOR.md` e `docs/DECISIONS.md`
(2026-09-17). Nenhum dado pessoal do print foi reproduzido no repositório
(ver `.claude/rules/homologacao-dados.md`).

Pendências restantes para desbloquear produção: arquivo físico do layout,
planilhas reais Matriz/Filial, confirmação da chave de matching, código do
evento da Cesta da Matriz, versão do conversor.

## Próximo passo

Obter o **arquivo físico** (não print) do layout já aceito pelo Questor —
colocar em `homologacao/art_latex/questor/layout_aceito/` (fica só local,
nunca versionado — ver `.claude/rules/homologacao-dados.md`) e registrar
hash SHA-256 em `homologacao/art_latex/questor/evidencia/manifest.json`.
Em seguida, planilhas reais de origem (Matriz/Filial).

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
