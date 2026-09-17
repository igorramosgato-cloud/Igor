# Estado do projeto

**Atualizado em:** 2026-09-17

## Onde estamos

Roadmap item 1 (Variáveis + Benefícios → Questor, cliente ART LATEX) em
andamento. Regras de negócio parametrizadas e testadas (40/40 testes
passando).

**Gate de layout do Questor: PASS** (2026-09-17) — contrato físico
certificado por análise binária de arquivo real. Ver
`src/jrdp/questor_layout.py`.

**Planilhas de origem reais (Matriz e Filial) recebidas e inventariadas**
(2026-09-17), mas revelaram um **novo bloqueio, mais sério que os
anteriores**: a coluna de código do funcionário está vazia em 100% dos
registros reais, em todas as abas com dado, nos dois arquivos. A única
identificação disponível é nome livre — isso viola
`.claude/rules/matching.md` diretamente. **Nenhum mapeamento
origem→Questor será implementado até isso ser esclarecido.**

Duas divergências também registradas (não resolvidas silenciosamente):
1. A coluna da Cesta Básica da Matriz, que uma decisão anterior (baseada
   em memória) associava a "coluna E Desconto", na planilha real tem
   cabeçalho `CR`, não `Desconto`. Código do evento continua PENDENTE.
2. O arquivo recebido como "Filial" tem cabeçalho interno dizendo
   "MATRIZ" em várias abas — identidade do arquivo não confirmada.

Detalhes completos em `docs/P01_ART_LATEX_QUESTOR.md` e
`docs/DECISIONS.md` (entradas de 2026-09-17). Nenhum dado pessoal (nomes,
CPF, códigos, valores) dos arquivos reais foi reproduzido em qualquer
lugar versionado — ver `.claude/rules/homologacao-dados.md`.

## Próximo passo

**Esclarecer com o usuário** (não é uma decisão técnica que eu deva tomar
sozinho) como o matching funciona na prática: existe um cadastro mestre
código+nome separado destes dois arquivos? A macro VBA embutida faz esse
de-para ao gerar? O preenchimento do código é manual pela equipe de DP?

Sem essa resposta, o roadmap do P01 fica parado no passo "mapeamento
origem → Questor" — o gate de layout (passo anterior) já passou.

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
