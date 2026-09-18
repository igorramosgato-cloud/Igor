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

**Identidade homologada (60 pessoas) e códigos de evento da Matriz
confirmados (2026-09-18)**: a planilha `revisao_depara_nomes_HOMOLOGADA.xlsx`
voltou com as 60 linhas em `APROVAR` (literal), `Aprovado por="Igor"`,
`Data aprovação="2026-09-17"`, todas completas, e foi importada/mesclada
no de-para local (`depara_nomes.json`, fora do Git). Em seguida o
usuário confirmou que os códigos 1955 (VR), 813 (Compras), 806
(Farmácia) e 96 (Adicional Noturno) valem tanto para Filial quanto para
Matriz (mesmo padrão do 1524/Cesta) — `config/clientes/art_latex.json`
e `.claude/rules/art-latex.md` atualizados.

**Reprocessamento com Matriz+Filial nos 5 eventos revelou uma
pendência nova**: ao incluir os dados reais da Matriz, os eventos 96 e
1955 passaram a ter pessoas `NOT_FOUND` inéditas (14 e 11
respectivamente) que não faziam parte das 60 já homologadas — porque a
extração e a consolidação de identidade anteriores só tinham rodado
sobre a Filial para esses 4 eventos. Isso é esperado e correto: o
fail-closed por evento pegou a ampliação de escopo e voltou a bloquear
em vez de assumir que a mesma lista de 60 cobria todo mundo.

**Status atual, três camadas separadas (correção de terminologia
2026-09-18 — o "5/5 PASS" anterior media só o gate de identidade e não
deve ser lido como liberação de produção):**

| Evento | IDENTIDADE | EXPORTAÇÃO V | PRODUÇÃO |
|---|---|---|---|
| 806 Farmácia | PASS | ELEGÍVEL PARA HOMOLOGAÇÃO (candidato gerado) | BLOCKED |
| 813 Compras | PASS | ELEGÍVEL PARA HOMOLOGAÇÃO (candidato gerado) | BLOCKED |
| 1524 Cesta Básica | PASS | ELEGÍVEL PARA HOMOLOGAÇÃO (candidato gerado) | BLOCKED |
| 96 Adicional Noturno | BLOCKED (14 novos NOT_FOUND na Matriz) | BLOCKED | BLOCKED |
| 1955 VR | BLOCKED (11 novos NOT_FOUND na Matriz) | BLOCKED | BLOCKED |

Para 806/813/1524: candidatos `.csv` tipo V gerados em
`homologacao/art_latex/questor/homologacao_v_candidatos/` (fora do
Git), nomeados `CANDIDATO_HOMOLOGACAO_evento_<N>_competencia_08-2026.csv`
— nunca chamados de "final"/"produção"/"oficial". Cada um foi validado
por round-trip contra o contrato físico certificado
(`questor_layout.parse_arquivo_layout`) e por reconciliação
origem→canônico→CSV em quantidade e valor (Decimal, nunca float) —
todos batendo exatamente. Para 1524, Matriz e Filial também batem
separadamente antes do total combinado. Manifesto completo (JSON) em
`homologacao_v_candidatos/manifesto_homologacao.json` (fora do Git).

`QuestorExporterH` continua bloqueado incondicionalmente (sem
certificação binária tipo H). Nenhum CSV foi submetido ao Questor;
nenhuma importação automática foi feita; `GERAR_PARA_O_QUESTOR.bat`
não foi tocado.

Detalhes completos em `docs/DECISIONS.md` (entradas de 2026-09-17 e
2026-09-18). Nenhum dado pessoal foi reproduzido em qualquer lugar
versionado.

**Confirmação final do usuário (2026-09-18)**: os códigos 96, 806,
813, 1955, 1524 são os mesmos em Matriz e Filial — confirmado de forma
direta e explícita, config **não revertida**. O código 50 (HE 100%
Noturna) também vale para as duas unidades — adicionado à Filial em
`config/clientes/art_latex.json` (continua tipo hora, bloqueado por
`QuestorExporterH`, sem relação com esta confirmação). Os `NOT_FOUND`
novos de 96/1955 são reais, não erro de leitura, e seguem para o
mesmo fluxo de identidade já usado nas 60 pessoas anteriores.

**Planilha de revisão de identidade para 96/1955 gerada
(2026-09-18)**: 22 pessoas únicas (deduplicadas entre os dois eventos
— 14 aparecem em 96, 11 em 1955, com sobreposição), todas unidade
`matriz`, todas com sugestão fuzzy diagnóstica (nenhuma sem
candidato). Planilha real em
`homologacao/art_latex/questor/depara/revisao_depara_nomes_96_1955.xlsx`
(fora do Git). **Nenhuma decisão preenchida** — trabalho do analista de
DP, mesmo fluxo já usado para as 60 pessoas anteriores.

## Próximo passo

Duas frentes independentes:
1. **96 e 1955**: analista de DP revisa
   `revisao_depara_nomes_96_1955.xlsx` (22 pessoas), homologa
   (`APROVAR` + responsável + data). Depois:
   `revisao_depara.importar_decisoes_aprovadas` →
   `depara.mesclar_depara`/`salvar_depara` → reexecutar 96 e 1955 → se
   100% resolvidos, gerar candidatos V e submeter ao mesmo gate de
   reconciliação já aplicado a 806/813/1524.
2. **806, 813, 1524**: decidir com o usuário quando submeter
   manualmente os 3 candidatos já elegíveis para o teste real de
   importação no Questor (fora desta automação) — só depois de um
   sucesso confirmado manualmente é que entram em consideração para
   qualquer automação de produção.

Em paralelo, seguem PENDENTES sem depender deste gate: `.csv` real
tipo H para certificação binária, versão do Questor, dados de
Vale-transporte (815).

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
