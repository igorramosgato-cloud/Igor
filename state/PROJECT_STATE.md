# Estado do projeto

**Atualizado em:** 2026-09-17

## Onde estamos

Roadmap item 1 (Variáveis + Benefícios → Questor, cliente ART LATEX) em
andamento. Regras de negócio parametrizadas e testadas (62/62 testes
passando).

Cinco pendências resolvidas pelo usuário nesta sessão:

1. **Código da Cesta Básica da Matriz confirmado: 1524** (mesmo código da
   Filial, natureza de desconto). `config/clientes/art_latex.json`
   atualizado.
2. **Identidade do arquivo "Filial" esclarecida** — não é erro; a
   intenção é gerar um único arquivo por evento, combinando Matriz e
   Filial.
3. **Regra H,MM confirmada para eventos tipo H** (ex.: `07:31` → `7,31`),
   já coberta pelo `serialize_hmm` existente, sem alteração de código.
4. **Cruzamento nome→código implementado**: `src/jrdp/origem_matching.py`
   cruza planilhas de origem (só nome) contra o cadastro de ativos
   (`cadastro_ativos.py`), bloqueando explicitamente nomes ambíguos ou
   não encontrados — nunca resolvendo por adivinhação. Validado contra
   dados reais: 117 nomes na Cesta Básica da Matriz, 114 resolvidos, 0
   ambíguos, 3 não encontrados.

**Gate de layout do Questor: PASS** (tipo V certificado por análise
binária; tipo H com regra de negócio confirmada, mas sem certificação
binária de arquivo real ainda).

Ainda falta para desbloquear a geração de produção:
- Implementar o pipeline completo (extrair valores reais de cada aba de
  benefício, resolver código via `origem_matching`, decidir o que fazer
  com nomes não encontrados, combinar Matriz+Filial em um único arquivo
  por evento).
- Decidir a precisão decimal real do valor no gerador (evidência física
  mostra precisão variável sem padding).
- Confirmar versão específica do Questor/layout do conversor.
- Certificação binária de um arquivo `.csv` real com `tipo=H`.

Detalhes completos em `docs/P01_ART_LATEX_QUESTOR.md` e
`docs/DECISIONS.md` (entradas de 2026-09-17). Nenhum dado pessoal (nomes,
CPF, códigos, valores) dos arquivos reais foi reproduzido em qualquer
lugar versionado — ver `.claude/rules/homologacao-dados.md`.

## Próximo passo

Implementar o pipeline de geração origem → Questor propriamente dito,
usando os módulos já certificados (`questor_layout`, `cadastro_ativos`,
`origem_matching`). Decidir antes o que fazer com nomes não encontrados no
cruzamento (bloquear a geração inteira? gerar parcial e reportar? isso não
foi definido ainda).

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
