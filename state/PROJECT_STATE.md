# Estado do projeto

**Atualizado em:** 2026-09-17

## Onde estamos

Roadmap item 1 (Variáveis + Benefícios → Questor, cliente ART LATEX) em
andamento. Regras de negócio parametrizadas e testadas (51/51 testes
passando).

**Gate de layout do Questor: PASS** (2026-09-17) — contrato físico
certificado por análise binária de arquivo real. Ver
`src/jrdp/questor_layout.py`.

**Planilhas de origem reais (Matriz e Filial) recebidas e inventariadas**
(2026-09-17). Revelaram bloqueio de matching (coluna de código do
funcionário vazia em 100% dos registros reais) — **resolvido no mesmo
dia**: o usuário forneceu um relatório real de cadastro ("Base de
ativos", Contrato/Nome/Admissão/Descrição/CPF, 495 registros) e confirmou
explicitamente que `Contrato` é o mesmo código usado como `COD. FUNC.
QUESTOR`. Implementado em `src/jrdp/cadastro_ativos.py`, testado e
validado em memória contra o arquivo real (495/495).

Duas divergências continuam registradas sem resolução (não bloqueiam mais
o matching, mas seguem pendentes):
1. Cesta Básica da Matriz: coluna real é `CR`, não `Desconto` como uma
   decisão anterior (baseada em memória) registrava. Código do evento
   continua PENDENTE.
2. O arquivo recebido como "Filial" tem cabeçalho interno dizendo
   "MATRIZ" em várias abas — identidade do arquivo não confirmada.

Detalhes completos em `docs/P01_ART_LATEX_QUESTOR.md` e
`docs/DECISIONS.md` (entradas de 2026-09-17). Nenhum dado pessoal (nomes,
CPF, códigos, valores) dos arquivos reais foi reproduzido em qualquer
lugar versionado — ver `.claude/rules/homologacao-dados.md`.

## Próximo passo

Com layout certificado e matching resolvido, o próximo passo é o
**mapeamento origem → Questor** propriamente dito: cruzar as planilhas
Matriz/Filial (só têm nome) contra o índice `cadastro_ativos` (nome/CPF →
contrato) e montar os registros no formato certificado por
`questor_layout`. Antes de implementar isso, ainda faltam: código do
evento da Cesta Básica da Matriz, esclarecimento da identidade do arquivo
Filial, confirmação do contrato de layout para eventos tipo `H`, e decisão
sobre precisão decimal do valor.

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
