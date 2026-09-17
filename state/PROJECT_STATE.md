# Estado do projeto

**Atualizado em:** 2026-09-17

## Onde estamos

Roadmap item 1 (Variáveis + Benefícios → Questor, cliente ART LATEX) em
andamento. Regras de negócio parametrizadas e testadas (40/40 testes
passando). Geração de arquivo de produção continua `BLOCKED`, mas o
**gate de certificação física do layout do Questor passou (PASS)** em
2026-09-17.

Certificado por análise binária de um arquivo `.csv` real (não Excel):
encoding CP850, delimitador `;`, terminador CRLF, sem BOM/aspas, estrutura
de 3 linhas de cabeçalho (código do evento, tipo, cabeçalho de colunas) +
registros + padding. Implementado em `src/jrdp/questor_layout.py`,
testado com fixture 100% sanitizada. Nenhum dado do arquivo real foi
reproduzido em qualquer lugar versionado — ver
`.claude/rules/homologacao-dados.md`. Detalhes em
`docs/P01_ART_LATEX_QUESTOR.md` e `docs/DECISIONS.md` (2026-09-17).

Conflito registrado (não resolvido): a evidência física mostra que o valor
não tem precisão decimal fixa, divergindo da regra atual de
`serializers.serialize_valor` (sempre 2 casas). Só será decidido quando o
gerador ART LATEX → Questor for implementado.

Pendências restantes para desbloquear produção: planilhas reais
Matriz/Filial da ART LATEX, confirmação da chave de matching, código do
evento da Cesta da Matriz, versão do conversor, e confirmação de que
eventos tipo `H` seguem o mesmo contrato de layout.

## Próximo passo

Planilhas reais de origem da ART LATEX (Matriz/Filial) — colocar em
`homologacao/art_latex/questor/origem/` (fica só local, nunca versionado).
A partir daí, iniciar o mapeamento origem → Questor (ainda não o gerador
completo).

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
