# Estado do projeto

**Atualizado em:** 2026-09-17

## Onde estamos

Roadmap item 1 (Variáveis + Benefícios → Questor, cliente ART LATEX) em
andamento. Regras de negócio parametrizadas e testadas (98/98 testes
passando, excluindo os dois arquivos com dependências ausentes no
ambiente).

Por pedido explícito do usuário, o foco desta etapa foi **fechar o
contrato físico do serializer antes do pipeline**, para não haver
retrabalho na camada crítica. Resultado:

- **Precisão decimal (tipo V)**: caracterização refinada — não é "N casas
  variáveis", é "nenhum arredondamento aplicado, valor bruto do cálculo
  gravado como está". `serialize_valor` continua divergente (2 casas
  fixas); mudança de código fica para quando o gerador for implementado.
- **Certificação binária tipo H**: **PENDENTE**, genuinamente sem
  evidência — não existe no acervo nenhum `.csv` real com `tipo=H`
  aceito pelo Questor. A regra de negócio (H,MM) já está confirmada
  separadamente e não muda.
- **Versão do Questor/importador**: **PENDENTE**, sem evidência nos
  artefatos disponíveis (metadados OOXML e strings do VBA dos `.xlsm`
  revelam só a macro `GerarLayoutImportacao`, nenhuma versão numérica).
- **Política de matching fail-closed**: adotada e implementada —
  `avaliar_gate_matching` em `src/jrdp/origem_matching.py` bloqueia a
  geração de produção com qualquer nome ambíguo ou não encontrado (mesmo
  1 de 117), sempre permitindo gerar o relatório de conferência. 6 testes
  permanentes travando esse comportamento.

Pendências resolvidas em rodadas anteriores da sessão (2026-09-17):
código da Cesta Básica da Matriz (1524), identidade do arquivo Filial
(intencional — objetivo é 1 arquivo por evento combinando Matriz+Filial),
cadastro de ativos (código↔nome↔CPF) e cruzamento nome→código.

Detalhes completos em `docs/P01_ART_LATEX_QUESTOR.md` e
`docs/DECISIONS.md` (entradas de 2026-09-17). Nenhum dado pessoal dos
arquivos reais foi reproduzido em qualquer lugar versionado — ver
`.claude/rules/homologacao-dados.md`.

## Próximo passo

Dois itens dependem só do usuário, não de mais análise:
1. Fornecer um arquivo `.csv` real com `tipo=H` aceito pelo Questor, para
   certificação binária (mesmo nível de rigor que o tipo V já recebeu).
2. Informar a versão do Questor Desktop/importador, se souber — os
   artefatos técnicos disponíveis não revelam isso.

Depois disso, o pipeline de geração origem→Questor pode ser implementado
sem risco de retrabalho na camada de serialização.

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
