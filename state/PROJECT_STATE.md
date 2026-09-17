# Estado do projeto

**Atualizado em:** 2026-09-17

## Onde estamos

Roadmap item 1 (Variáveis + Benefícios → Questor, cliente ART LATEX) em
andamento. 122/122 testes passando (excluindo os dois arquivos com
dependências ausentes no ambiente).

**Correção importante desta rodada**: a caracterização anterior de "sem
arredondamento" para valores tipo V foi refinada — usar `Decimal`, nunca
`float`, para nunca vazar artefato binário (`Decimal(19.1)` produz um
número de 50+ dígitos que a evidência real nunca mostrou). Implementado em
`src/jrdp/decimais.py`, com teste explícito do contra-exemplo clássico.

**Camada canônica do pipeline construída e testada**, sem liberar
produção: `canonico.py` (modelo `LancamentoCanonico` com rastreabilidade
completa), `pipeline.py` (matching + regra + serialização),
`conferencia.py` (relatório PASS/BLOCKED por evento, sempre gerável),
`exportadores.py` (`QuestorExporterV` fail-closed; `QuestorExporterH`
bloqueado incondicionalmente). Validado contra dados reais: Cesta Básica
da Matriz (117 nomes) → `BLOCKED`, 114 encontrados, 3 não encontrados,
exportação recusada — exatamente o comportamento fail-closed desejado.

Continuam **genuinamente PENDENTES**, sem evidência disponível:
- Certificação binária de um `.csv` real com `tipo=H` (não existe esse
  arquivo no acervo; não foi inferido do tipo V).
- Versão do Questor/importador (metadados dos `.xlsm` e strings do VBA
  não revelam isso).

Detalhes completos em `docs/P01_ART_LATEX_QUESTOR.md` e
`docs/DECISIONS.md` (entradas de 2026-09-17). Nenhum dado pessoal dos
arquivos reais foi reproduzido em qualquer lugar versionado — ver
`.claude/rules/homologacao-dados.md`. Nenhum exportador foi ligado a
`GERAR_PARA_O_QUESTOR.bat` ou à CLI — o `BLOCKED` global do P01 continua
valendo.

## Próximo passo

Dois itens dependem só do usuário:
1. Fornecer um arquivo `.csv` real com `tipo=H` aceito pelo Questor.
2. Informar a versão do Questor Desktop/importador, se souber.

Em paralelo, sem depender do usuário: implementar a extração real das
demais abas de benefício (Vale-refeição, Vale-compras, convênio
farmácia, Adicional Noturno) usando a camada canônica já pronta, e
decidir o fluxo operacional de correção quando o gate de matching fica
BLOCKED.

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
