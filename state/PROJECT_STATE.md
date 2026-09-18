# Estado do projeto

**Atualizado em:** 2026-09-18

## Onde estamos

Roadmap item 1 (Variáveis + Benefícios → Questor, cliente ART LATEX) em
andamento. **200/200 testes passando** (excluindo os dois arquivos com
dependências ausentes no ambiente).

**Correção de escopo do de-para**: agora é por **cliente+unidade+nome**,
nunca só nome+unidade — evita reaproveitar uma correspondência da Filial
para a Matriz, ou de um cliente para outro, por acidente.

**Planilha de revisão de identidade gerada** (não preenchida):
`homologacao/art_latex/questor/depara/revisao_depara_nomes.xlsx` (fora
do Git), com as 60 pessoas reais não encontradas — 54 com sugestão
automática (fuzzy, corte 0,6), 6 sem candidato (busca manual). Colunas:
Nome origem, Unidade, Eventos, Sugestão, Código sugerido, Nome cadastro,
Confiança diagnóstica, Decisão analista, Aprovado por, Data aprovação,
Observação. **Nenhuma decisão foi preenchida** — isso é trabalho do
analista de DP.

Novo módulo `src/jrdp/revisao_depara.py`: gera a planilha
(`escrever_planilha_revisao`) e importa só as linhas marcadas
`"APROVAR"` com aprovador/data preenchidos
(`importar_decisoes_aprovadas`) — qualquer coisa incompleta é erro, não
suposição.

**Revisão de identidade por evidência documental (2026-09-18)**: as 60
pessoas foram cruzadas contra Base Questor, recibos 08/2026,
admissões/cadastros e Relação de Eventos (revisão assistida por IA, não
homologação). Resultado: 60 `RECOMENDAR_APROVAR`, 0 `APROVAR`,
`Aprovado por`/`Data aprovação` vazios em 100% — o valor `APROVAR` fica
reservado exclusivamente à homologação humana, evitando a ambiguidade
da leva anterior. 2 casos (ANA CAROLINE SABINO, KAYLANE DE OLIVEIRA
MENDONÇA) tinham divergência entre unidade de origem (filial) e lotação
cadastral atual (Matriz); o usuário confirmou diretamente que essa
divergência não bloqueia a identidade desses 2 casos — decisão
registrada em `docs/DECISIONS.md` (2026-09-18). Isso não homologa
nenhuma correspondência; nenhuma importação de de-para foi feita.

**Identidade homologada e 5 eventos reexecutados, todos PASS
(2026-09-18)**: a planilha `revisao_depara_nomes_HOMOLOGADA.xlsx` voltou
com as 60 linhas em `APROVAR` (literal), `Aprovado por="Igor"`,
`Data aprovação="2026-09-17"`, todas completas. Sequência executada:
`revisao_depara.importar_decisoes_aprovadas` → `depara.mesclar_depara`/
`salvar_depara` (`depara_nomes.json` local, fora do Git, confirmado via
`git check-ignore`) → reexecução dos 5 eventos do pacote contra os
arquivos reais. Resultado: **96, 806, 813, 1524, 1955 todos em `PASS`**
(0 NOT_FOUND, 0 AMBIGUOUS, 0 inválidos cada); manifesto **TOTALMENTE
LIBERADO**. Consolidado: 412 pessoas únicas, 352 por match exato, 60
por de-para homologado, 0 pendentes, 0 ambíguas. Detalhe completo em
`docs/DECISIONS.md` (2026-09-18).

Importante: `PASS` aqui é o relatório de conferência
(`RelatorioEvento.pode_exportar()==True`) — **nenhum `.csv` de produção
foi gerado ainda** via `QuestorExporterV` nesta sessão.

Continuam PENDENTES, sem relação com o gate de identidade: certificação
binária tipo H, versão do Questor, Vale-transporte, códigos de evento
da Matriz para as 4 abas (VR/Compras/Farmácia/Adicional Noturno — só
rodadas na Filial; a Matriz não tem código confirmado para elas).

Detalhes completos em `docs/P01_ART_LATEX_QUESTOR.md` e
`docs/DECISIONS.md` (entradas de 2026-09-17 e 2026-09-18). Nenhum dado
pessoal foi reproduzido em qualquer lugar versionado. Nenhum exportador
ligado à produção ainda foi acionado — `BLOCKED` global do P01 continua
valendo pelos itens PENDENTES acima.

## Próximo passo

Decidir com o usuário se/quando gerar os `.csv` de produção dos 5
eventos já `PASS` (96, 806, 813, 1524, 1955) via `QuestorExporterV`, e
planejar a homologação formal do processo (`/homologar-automacao`)
antes de qualquer uso em operação real. Em paralelo, seguem PENDENTES
sem depender deste gate: (1) obter/confirmar códigos de evento da
Matriz para as 4 abas restantes; (2) obter um `.csv` real tipo H para
certificação binária; (3) confirmar versão do Questor; (4) resolver a
ausência de dados de Vale-transporte.

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
