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

Continuam PENDENTES: certificação binária tipo H, versão do Questor,
Vale-transporte, códigos de evento da Matriz para 4 abas.

Detalhes completos em `docs/P01_ART_LATEX_QUESTOR.md` e
`docs/DECISIONS.md` (entradas de 2026-09-17). Nenhum dado pessoal foi
reproduzido em qualquer lugar versionado. Nenhum exportador ligado à
produção — `BLOCKED` global do P01 continua valendo.

## Próximo passo

Trabalho humano: um analista de DP abre
`homologacao/art_latex/questor/depara/revisao_depara_nomes.xlsx`
localmente, confirma ou rejeita cada uma das 60 sugestões (ou busca
manualmente as 6 sem candidato), preenche `Decisão analista`
(`APROVAR`/`REJEITAR`), `Aprovado por` e `Data aprovação`, e salva.

Depois disso, rodar `revisao_depara.importar_decisoes_aprovadas` sobre a
planilha revisada, mesclar com `depara.mesclar_depara`, salvar com
`depara.salvar_depara`, e reexecutar os 5 eventos — os que ficarem 100%
resolvidos passam a `PASS` no manifesto e podem ser gerados pelo
`QuestorExporterV`, independentemente dos demais.

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
