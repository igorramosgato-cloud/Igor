# Decisões

Entradas mais recentes no topo. Formato definido em
`.claude/skills/registrar-decisao/SKILL.md`.

## 2026-09-18 — Confirmação final: códigos 96/806/813/1955/1524/50 valem para Matriz E Filial; config mantida

**Contexto:** após o reprocessamento anterior (Matriz+Filial nos 5
eventos de valor + NOT_FOUND novos em 96/1955), havia risco de
interpretar isso como um possível erro de leitura da confirmação
anterior e reverter `config/clientes/art_latex.json`.

**Decisão:** o usuário confirmou de forma direta, explícita e final
que:
- 96 (Adicional Noturno), 806 (Farmácia), 813 (Compras), 1955 (VR) e
  1524 (Cesta Básica) são os mesmos códigos em Matriz e Filial — a
  config atual está correta, **não deve ser revertida**.
- 50 (HE 100% Noturna) também vale para Matriz **e** Filial — antes só
  estava registrado na Matriz.
- Os `NOT_FOUND` novos encontrados na Matriz para 96 e 1955 são reais
  (pessoas de fato não resolvidas pelo match exato nem pelo de-para já
  homologado) e devem seguir o mesmo fluxo de identidade já usado para
  as 60 pessoas anteriores — não é motivo para desfazer a config.
- Os candidatos V já gerados para 806, 813 e 1524 continuam válidos.

**Impacto:** `config/clientes/art_latex.json` — evento 50 (HE 100%
Noturna) adicionado também à unidade `filial` (continua tipo `hora`,
sujeito ao bloqueio geral de `QuestorExporterH`, sem relação com esta
confirmação). Nenhuma outra mudança de config — os eventos
96/806/813/1955/1524 de Matriz+Filial já registrados na decisão
anterior (mesma data) permanecem exatamente como estavam.
`.claude/rules/art-latex.md` atualizado com o código 50 na tabela da
Filial.

Próximo trabalho: nova rodada de revisão de identidade (mesmo fluxo
`revisao_depara.py`) só para os `NOT_FOUND` novos da Matriz de 96 e
1955, sem duplicar pessoas que apareçam nos dois eventos.

**Evidência:** confirmação textual direta e explícita do usuário nesta
conversa em 2026-09-18, respondendo ao relatório do reprocessamento
anterior.

## 2026-09-18 — Homologação formal dos eventos V + geração de candidatos (taxonomia IDENTIDADE/EXPORTAÇÃO V/PRODUÇÃO)

**Contexto:** execução do gate "homologação formal dos eventos V +
geração de arquivos candidatos", pedido explicitamente pelo usuário,
com correção de terminologia: o "5/5 PASS" registrado antes media só
`IDENTIDADE`/`MATCHING` e não deveria ter sido lido como liberação de
produção — `TOTALMENTE LIBERADO` era forte demais para o que de fato
estava certificado.

**Decisão:** adotada a taxonomia de 3 camadas por evento:

- **IDENTIDADE** — match exato + de-para, sem `NOT_FOUND`/`AMBIGUOUS`/
  inválido.
- **EXPORTAÇÃO V** — candidato `.csv` gerado, contrato físico validado
  por round-trip contra `questor_layout.parse_arquivo_layout` (já
  certificado, não alterado), e reconciliação origem→canônico→CSV em
  quantidade e valor via `Decimal` (nunca float).
- **PRODUÇÃO** — sempre `BLOCKED` nesta automação: nenhuma importação
  real ou automática é feita por ela.

Ao incluir a Matriz nos 4 eventos recém-confirmados (1955, 813, 806,
96 — ver decisão anterior desta mesma data), a extração revelou
pessoas `NOT_FOUND` inéditas em 2 deles (96: 14 pessoas; 1955: 11
pessoas) que não faziam parte das 60 já homologadas — a
extração/consolidação anterior só tinha rodado sobre a Filial para
essas 4 abas.

**Resultado por evento:**

| Evento | IDENTIDADE | EXPORTAÇÃO V | PRODUÇÃO |
|---|---|---|---|
| 806 Farmácia | PASS | ELEGÍVEL PARA HOMOLOGAÇÃO | BLOCKED |
| 813 Compras | PASS | ELEGÍVEL PARA HOMOLOGAÇÃO | BLOCKED |
| 1524 Cesta Básica (Matriz+Filial) | PASS | ELEGÍVEL PARA HOMOLOGAÇÃO | BLOCKED |
| 96 Adicional Noturno | BLOCKED (14 NOT_FOUND novos da Matriz) | BLOCKED | BLOCKED |
| 1955 VR | BLOCKED (11 NOT_FOUND novos da Matriz) | BLOCKED | BLOCKED |

Reconciliação (Decimal, origem = canônico = csv, em quantidade e
valor):
- 806: 11 = 11 = 11 registros, R$ 985,96 nas três camadas.
- 813: 24 = 24 = 24 registros, R$ 1.501,28 nas três camadas.
- 1524: 317 = 317 = 317 registros, total 317 (R$1,00/colaborador);
  Matriz 117 registros/R$117, Filial 200 registros/R$200, batendo
  separadamente antes do total combinado.

Contrato físico `PASS` nos 3 candidatos gerados. Nenhum CSV tipo H foi
gerado (`QuestorExporterH` continua bloqueado incondicionalmente).
Nenhuma importação automática no Questor foi feita.
`GERAR_PARA_O_QUESTOR.bat` não foi alterado. Os 3 candidatos (806, 813,
1524) e o manifesto de homologação completo (JSON com cobertura,
reconciliação e SHA-256 de cada candidato) ficam em
`homologacao/art_latex/questor/homologacao_v_candidatos/`, fora do Git
(confirmado via `git check-ignore`), nomeados explicitamente
`CANDIDATO_HOMOLOGACAO_...` — nunca "final"/"produção"/"oficial".

**Checklist `/homologar-automacao` aplicado a este escopo:**
1. Dados de origem são os arquivos reais já inventariados em
   `evidencia/manifest.json` — uso aqui é só geração de candidato para
   revisão manual, não operação.
2. 200/200 testes passando; nenhum código de biblioteca certificado
   foi alterado (só `config/clientes/art_latex.json`, mais a
   orquestração no script de reexecução, que reusa
   `QuestorExporterV`/`questor_layout.py` sem modificá-los).
3. Rastreabilidade: manifesto de homologação registra
   origem→decisão→saída por evento.
4. Evidência de saída real validada por humano: **AINDA NÃO** — os
   candidatos ainda não foram submetidos manualmente ao Questor,
   então **a homologação não pode ser considerada concluída para fins
   de liberação de produção**.
5. Pendências explícitas (96, 1955, tipo H, versão Questor, VT)
   continuam bloqueando a geração de arquivos de produção para os
   casos que dependem delas.

**Evidência:** script de reexecução rodado nesta sessão em 2026-09-18
contra os arquivos reais (`planilha_importacao_matriz.xlsm`,
`planilha_importacao_filial.xlsm`, `base_ativos_art_latex.csv`,
`depara_nomes.json` homologado); `manifesto_homologacao.json` local
com detalhamento completo por evento.

**Impacto:** `state/tasks.json` e `state/PROJECT_STATE.md` atualizados
com a tabela de 3 camadas por evento e os próximos passos (nova
rodada de identidade para 96/1955; decisão do usuário sobre submissão
manual dos 3 candidatos elegíveis ao teste real de importação no
Questor). `P01` continua com status geral `blocked`.

## 2026-09-18 — Códigos de evento da Matriz para VR/Compras/Farmácia/Adicional Noturno confirmados (mesmos da Filial)

**Contexto:** os eventos VR (1955), Compras (813), Farmácia (806) e
Adicional Noturno (96) tinham dados reais nas abas correspondentes da
Matriz (`Vale-refeicao`: 123 linhas, `Vale-compras`: 3, `convenio
farmacia`: 4, `Adicional Noturno`: 72 — mesma estrutura de colunas
`COD. FUNC.`/`NOME`/`VALOR` da Filial, cabeçalho na linha 5, dados a
partir da linha 6), mas sem código de evento confirmado para a Matriz
— status `PENDENTE`, dados da Matriz não usados no pipeline até agora.

**Decisão:** o usuário confirmou diretamente, nesta conversa, que os
mesmos códigos já usados na Filial (1955 VR, 813 Compras, 806
Farmácia, 96 Adicional Noturno) valem também para a Matriz — não são
eventos exclusivos da Filial, é o mesmo código de evento nas duas
unidades (mesmo padrão evidencial já usado para o código 1524 da Cesta
Básica, confirmado em 2026-09-17).

`config/clientes/art_latex.json` atualizado: a unidade `matriz` ganhou
os 4 eventos, com os mesmos códigos e `tipo: "valor"` da Filial.
`.claude/rules/art-latex.md` atualizado com a tabela e a nota de
confirmação.

**Impacto:** o arquivo de importação combinado desses 4 eventos passa
a juntar Matriz+Filial (como já acontecia só para 1524/Cesta) — não
mais somente Filial. Isso exige reprocessar o pipeline: extrair os
registros da Matriz para essas 4 abas, combinar com os já extraídos da
Filial, rodar matching (exato + de-para já homologado) e gerar novo
relatório de conferência por evento. Nenhum CSV de produção foi gerado
ainda — a mudança foi feita antes da geração dos candidatos de
homologação tipo V, para que a cobertura correta (Matriz+Filial nos 5
eventos) já entre nos candidatos.

**Evidência:** confirmação textual direta do usuário nesta conversa em
2026-09-18 ("ESSES NUMEROS DE EVENTOS SÃO PARA A MATRIZ E FILIAL"),
interpretada e confirmada de volta ao usuário antes da alteração de
config, seguindo o mesmo padrão evidencial já usado para o código 1524
da Cesta Matriz.

## 2026-09-18 — Identidade homologada; 5 eventos do pacote reexecutados e em PASS

**Contexto:** as 60 correspondências de identidade não resolvidas pelo
match exato (processo P01, cliente ART LATEX) chegaram à etapa final da
sequência combinada anteriormente: homologação humana real.

**Decisão:** a planilha `revisao_depara_nomes_HOMOLOGADA.xlsx` foi
recebida com as 60 linhas marcadas com o literal `APROVAR` (não mais
`RECOMENDAR_APROVAR`), `Aprovado por = "Igor"`, `Data aprovação =
"2026-09-17"`, todas com código sugerido preenchido — verificação
estrutural confirmou 60/60 linhas completas, 0 incompletas. A partir
disso foi executada a sequência já combinada:

1. `revisao_depara.importar_decisoes_aprovadas` sobre a planilha
   homologada → 60 `RegistroDePara`.
2. `depara.mesclar_depara` (de-para local existente estava vazio) +
   `depara.salvar_depara` em
   `homologacao/art_latex/questor/depara/depara_nomes.json` (local,
   fora do Git — confirmado via `git check-ignore`).
3. Reexecução dos 5 eventos do pacote (96 Adicional Noturno, 806
   Farmácia, 813 Compras, 1524 Cesta Básica Matriz+Filial, 1955 VR)
   contra os arquivos reais (`planilha_importacao_matriz.xlsm`,
   `planilha_importacao_filial.xlsm`, `base_ativos_art_latex.csv`).

**Resultado: todos os 5 eventos passaram a `PASS`** (0 `NOT_FOUND`, 0
`AMBIGUOUS`, 0 inválidos, em cada um). Manifesto: **TOTALMENTE
LIBERADO** (5/5 gerados, 0 bloqueados).

Detalhe por evento (TOTAL / EXATO / DE-PARA):
- 96 Adicional Noturno: 44 / 33 / 11
- 806 Farmácia: 7 / 5 / 2
- 813 Compras: 21 / 16 / 5
- 1524 Cesta Básica (Matriz+Filial): 317 / 304 / 13
- 1955 VR: 233 / 190 / 43

Consolidado de pessoas (todas as unidades/eventos rodados): 412 pessoas
únicas, 352 resolvidas por match exato, 60 resolvidas por de-para
homologado, 0 ainda não resolvidas, 0 ambíguas.

**Isso não libera exportação de produção automaticamente.** `PASS`
aqui é o relatório de conferência (`RelatorioEvento.pode_exportar() ==
True`) — a geração efetiva do arquivo `.csv` via `QuestorExporterV`
para cada evento ainda não foi executada nesta sessão.
`QuestorExporterH` continua bloqueado incondicionalmente (sem
certificação binária tipo H). Continuam PENDENTE, sem relação com este
gate: códigos de evento da Matriz para VR/Compras/Farmácia/Adicional
Noturno (essas 4 abas só foram rodadas na Filial), VT (815), versão do
Questor.

**Evidência:** planilha real `revisao_depara_nomes_HOMOLOGADA.xlsx`
(fora do Git), aprovador "Igor", data "2026-09-17"; script de
reexecução rodado nesta sessão em 2026-09-18 contra os arquivos reais
já inventariados (`homologacao/art_latex/questor/evidencia/manifest.json`);
`depara_nomes.json` local gerado com 60 entradas.

**Impacto:** `state/tasks.json` e `state/PROJECT_STATE.md` atualizados
para refletir o gate de identidade como homologado e os 5 eventos do
pacote como `PASS` no relatório de conferência. `P01` continua com
status geral `blocked` pelos itens ainda PENDENTES listados acima —
nenhum arquivo de exportação de produção foi gerado ainda.

## 2026-09-18 — Divergência de unidade em 2 casos do de-para (ANA CAROLINE SABINO, KAYLANE DE OLIVEIRA MENDONÇA) não bloqueia identidade

**Contexto:** na revisão documental por evidência dos 60 nomes não
encontrados (processo P01, cliente ART LATEX), 2 casos — ANA CAROLINE
SABINO e KAYLANE DE OLIVEIRA MENDONÇA, ambos com unidade de origem
`filial` — tiveram identidade/código confirmados, mas a lotação
cadastral atual encontrada na evidência aponta `Matriz`, provavelmente
por transferência entre competências. Isso os deixou `PENDENTE` pela
política fail-closed padrão (unidade divergente).

**Decisão:** o usuário autorizou diretamente, nesta conversa, tratar
essa divergência de unidade como **não bloqueante para fins de
identidade no de-para**, apenas para esses 2 casos específicos. Regra
operacional:
- a unidade de origem (`filial`) é preservada como parte da chave do
  de-para (`cliente+unidade+nome`) — não é substituída por `Matriz`;
- a lotação cadastral atual (`Matriz`) é reconhecida e deve ficar
  registrada no campo `evidencia` da entrada de-para desses 2 casos,
  mas não impede a resolução da identidade;
- a exceção deve permanecer rastreável (nome, evidência da divergência,
  autorização do usuário, data).

Essa autorização substitui, para fins de governança, a anotação
equivalente que já existia dentro da planilha de revisão assistida por
IA (que não tem valor de decisão de negócio por si só) — a decisão
válida é esta confirmação direta do usuário.

**Isso NÃO homologa as 60 correspondências propostas pela revisão
assistida por IA.** Todas continuam como `RECOMENDAR_APROVAR` (0 com o
literal `APROVAR`, `Aprovado por`/`Data aprovação` vazios). Nenhuma
importação de de-para foi feita, nenhum código foi alterado. O próximo
gate continua sendo a homologação humana real (troca para `APROVAR` +
responsável + data) antes de rodar
`importar_decisoes_aprovadas` → `mesclar_depara` → `salvar_depara` →
reexecução dos 5 eventos.

**Evidência:** planilhas de revisão de identidade (fora do Git, dados
reais) — versão "VALIDADA_POR_EVIDENCIA" (os 2 casos como `PENDENTE`,
com observação textual da divergência de unidade) e versão
"PRONTA_PARA_HOMOLOGACAO" (mesmos 2 casos reclassificados como
`RECOMENDAR_APROVAR`); confirmação textual direta do usuário nesta
conversa em 2026-09-18.

**Impacto:** nenhum impacto em código ou dado versionado. Quando a
homologação humana ocorrer, esses 2 casos poderão ser aprovados
(`RECOMENDAR_APROVAR` → `APROVAR` + responsável + data) sem ficar presos
indefinidamente por causa da divergência de lotação — mas a homologação
em si ainda não ocorreu e continua sendo pré-requisito para qualquer
importação de de-para.

## 2026-09-17 — De-para por cliente+unidade+nome; planilha de revisão humana gerada

**Contexto:** operacionalizar a revisão das 60 pessoas não encontradas
para o analista de DP, e corrigir o escopo do de-para antes que ele fosse
usado de verdade.

**1) De-para agora é por cliente+unidade+nome, nunca só nome+unidade.**
`RegistroDePara` ganhou o campo `cliente` (obrigatório, nunca `"*"` —
diferente de `unidade`, que aceita `"*"` para valer nas duas unidades do
mesmo cliente). `depara.resolver_depara` e
`origem_matching.cruzar_com_depara` agora exigem `cliente` e só
resolvem quando bate exatamente. Isso evita reaproveitar uma
correspondência da Filial de um cliente para a Matriz, ou pior, para um
cliente diferente, só porque o nome de origem é textualmente igual.
Testado explicitamente (`test_cliente_errado_nunca_reaproveita_correspondencia`,
`test_depara_com_cliente_errado_nao_resolve`).

**2) Planilha de revisão de identidade — gerada, não preenchida por
mim.** Novo módulo `src/jrdp/revisao_depara.py`:
`montar_linhas_revisao` (junta cada ocorrência não encontrada com uma
sugestão fuzzy, quando existir) + `escrever_planilha_revisao` (`.xlsx`
local) + `importar_decisoes_aprovadas` (só linhas `"APROVAR"` com
aprovador e data preenchidos viram `RegistroDePara`; qualquer coisa
incompleta é erro, não suposição). Colunas: Nome origem, Unidade,
Eventos, Sugestão, Código sugerido, Nome cadastro, Confiança
diagnóstica, Decisão analista, Aprovado por, Data aprovação, Observação
— três colunas a mais que a proposta original (Aprovado por, Data
aprovação, Eventos) porque o schema do de-para exige essa evidência.
**Gerei a planilha real com os 60 casos reais, mas não preenchi nenhuma
decisão** — isso é julgamento humano, não meu.
**3) CSV tipo H e versão do Questor — sem mudança, seguem PENDENTE.**

**Validação real** (nenhum nome persistido em arquivo versionado): a
planilha real gerada em
`homologacao/art_latex/questor/depara/revisao_depara_nomes.xlsx` (fora
do Git, confirmado com `git check-ignore -v`) tem 60 linhas — **54 com
sugestão automática, 6 sem candidato** (para busca manual). Esse número
usa o corte padrão de similaridade do módulo (0,6); um diagnóstico
anterior, com corte mais rígido (0,75), havia mostrado 39/21 — são dois
recortes de confiança diferentes, não uma contradição.

**Evidência:** execução real dos módulos novos contra os arquivos já em
`homologacao/art_latex/questor/origem/`.
**Impacto:** `src/jrdp/depara.py` (campo `cliente`, `salvar_depara`,
`mesclar_depara`), `src/jrdp/origem_matching.py` (`cruzar_com_depara`
exige `cliente`), `src/jrdp/pipeline.py` (propaga `cliente`),
`src/jrdp/identidade.py` (`coletar_ocorrencias_nao_encontradas`),
`src/jrdp/revisao_depara.py` (novo). `tests/fixtures/questor/depara_sanitizado.json`
atualizada com `cliente`. 17 novos testes
(`test_revisao_depara.py`: 10, mais 7 entre `test_depara.py`/
`test_cruzar_com_depara.py`/`test_identidade.py` cobrindo cliente e
coleta por unidade). Nenhum de-para real foi homologado nesta sessão —
o pacote continua `TOTALMENTE BLOQUEADO` até a revisão humana acontecer.

## 2026-09-17 — Camada de identidade: de-para homologado, fail-closed por evento, quatro decisões fechadas

**Contexto:** com 5 eventos processados e todos `BLOCKED` por nomes não
encontrados, o usuário tomou quatro decisões de arquitetura para não
deixar o projeto esperando indefinidamente por itens externos.

**1) Eventos da Matriz sem código — continuam PENDENTE.** Não usar os
códigos da Filial por analogia. Vale-refeição, Compras, Farmácia e
Adicional Noturno da Matriz só entram em qualquer exportador depois de
evidência do código correto. Nenhuma mudança de código nesta entrada —
já estava assim desde a decisão anterior.

**2) Nomes não encontrados — de-para manual homologado, local, nunca
fuzzy automático.** Ordem de resolução, travada em código e teste:
`match exato normalizado → de-para homologado → NOT_FOUND/AMBIGUOUS`.
Implementado `src/jrdp/depara.py` (`RegistroDePara`, `carregar_depara`,
`resolver_depara`) e `src/jrdp/origem_matching.cruzar_com_depara`
(orquestra as duas etapas, nessa ordem, sempre). O arquivo real de
de-para (`homologacao/art_latex/questor/depara/depara_nomes.json`) fica
fora do Git — confirmado com `git add -A -n` que só o `README.md` seria
versionado. Cada entrada exige `evidencia`, `aprovado_por`, `aprovado_em`
— nunca "parece o mesmo nome" sem justificativa. Entradas `revogado`
ficam no histórico sem serem aplicadas.

**Diagnóstico fuzzy — implementado como sugestão, nunca como decisão.**
`src/jrdp/sugestao_fuzzy.py` (`sugerir_candidatos`, via `difflib`) só
gera candidatos para um analista revisar; não tem nenhum caminho de
código que alimente `ResultadoCruzamento.resolvidos` diretamente. Testado
explicitamente que o resultado não tem métodos `aplicar`/`resolver`.

**3) CSV tipo H e versão do Questor — continuam PENDENTE, sem travar o
resto.** Nenhuma mudança — `QuestorExporterH` segue bloqueando
incondicionalmente.

**4) Fail-closed por evento, não pelo pacote inteiro.** Implementado
`src/jrdp/manifesto.py` (`LinhaManifesto`, `ManifestoPacote`,
`gerar_manifesto`): cada evento aparece com seu próprio `PASS`/`BLOCKED`
no manifesto; o pacote é `TOTALMENTE LIBERADO`, `PARCIALMENTE LIBERADO`
ou `TOTALMENTE BLOQUEADO` dependendo da mistura. Um evento 100% resolvido
nunca fica refém de outro evento bloqueado — nem o inverso: um evento
com qualquer pendência nunca gera arquivo parcial (ex.: nunca um
`1955.csv` com 190 de 233 pessoas).

**Camada de identidade (novo módulo `src/jrdp/identidade.py`):**
`consolidar_nao_encontrados`/`contar_pessoas_unicas_nao_encontradas`
agrupam os NOT_FOUND de múltiplos eventos por nome normalizado — a mesma
pessoa em duas abas conta como uma, não duas.

**Validação real agregada** (só em memória, nenhum nome individual
persistido): dos 5 eventos já processados (1955, 813, 806, 96, 1524), a
soma bruta de "não encontrados" por evento é 74, mas consolidando por
pessoa isso cai para **60 pessoas únicas** — 11 delas aparecem como não
encontradas em mais de um evento (8 em dois eventos, 3 em três). Rodado
o diagnóstico fuzzy (só sugestão) sobre essas 60: **39 têm ao menos um
candidato plausível** no cadastro (provável correção de espaço/acento/
sobrenome), **21 não têm candidato próximo** (provável ausência real do
cadastro, precisa investigação separada, não é caso de de-para). O
manifesto do pacote, sem nenhuma entrada de de-para ainda, é
`TOTALMENTE BLOQUEADO` (0 de 5 eventos gerados) — esperado, pois nenhuma
correção foi homologada ainda.

**Evidência:** execução real dos módulos novos contra os arquivos já em
`homologacao/art_latex/questor/origem/`. Nenhum nome, CPF, código ou
valor individual foi reproduzido em qualquer arquivo do repositório —
só contagens agregadas.
**Impacto:** `src/jrdp/depara.py`, `src/jrdp/sugestao_fuzzy.py`,
`src/jrdp/identidade.py`, `src/jrdp/manifesto.py` (novos);
`src/jrdp/origem_matching.py` (`normalizar_nome` tornada pública,
`cruzar_com_depara` adicionada); `src/jrdp/pipeline.py` (parâmetro
`depara` opcional, retrocompatível). `homologacao/art_latex/questor/depara/`
(pasta nova, só README versionado). 34 novos testes
(`test_depara.py`: 12, `test_cruzar_com_depara.py`: 8,
`test_sugestao_fuzzy.py`: 4, `test_identidade.py`: 5,
`test_manifesto.py`: 5), fixture sanitizada
`tests/fixtures/questor/depara_sanitizado.json`. Nenhum exportador
ligado à produção; nenhuma correção real de de-para foi criada nesta
sessão (isso é trabalho do analista de DP, com evidência própria).

## 2026-09-17 — Extração real das demais abas; H,MM nunca é unidade aritmética; novo PENDENTE (eventos Matriz sem código)

**Contexto:** avançar a extração real das fontes ART LATEX (sem esperar o
CSV tipo H), construindo sobre a camada canônica já existente, sem
liberar produção.

**1) Conflito identificado e resolvido a favor da evidência física.** A
instrução recebida pedia "Matriz: utilizar o valor da coluna E
'Desconto'" para a Cesta Básica. Isso **contradiz** a entrada de decisão
de 2026-09-17 (mais abaixo), que já havia comprovado por evidência física
que a coluna E real é `CR`, não `Desconto`, e que a aba não tem nenhuma
coluna de valor. **Não segui a instrução textual** — implementei a regra
já confirmada (contagem de colaboradores listados, R$1,00 cada, igual à
Filial) e registro aqui a divergência, em vez de sobrescrever
silenciosamente.

**2) H,MM nunca é unidade aritmética — proteção permanente.** Somar
`"1,52" + "0,32"` como decimal daria `1,84`, que não corresponde a
nenhuma duração real (01:52 + 00:32 = 144 minutos = 02:24). Implementado
`src/jrdp/minutos.py` (`hhmm_para_minutos`, `minutos_para_hhmm`,
`somar_horas_em_minutos`) e usado em `conferencia.gerar_relatorio_evento`
para totalizar horas sempre via minutos, nunca via string serializada.
Teste permanente em `tests/test_minutos.py` prova explicitamente que a
soma decimal ingênua (`1,84`) diverge do resultado correto (`144`
minutos / `02:24`).

**3) Extratores reais implementados** (`src/jrdp/extratores/`):
- `valor_simples.py` — padrão `COD.FUNC/NOME/VALOR`, usado em
  Vale-refeição, Vale-compras, Convênio Farmácia, Adicional Noturno.
- `cesta_basica.py` — só nomes (valor é regra de negócio, não coluna).
- `horas.py` — Hora-extra (HE 50%/100%), **estrutural, não validado
  contra dados reais** (a aba segue com 0 registros reais nos dois
  arquivos). Suporte a `datetime.time`, string `HH:MM` e fração de dia
  (float) é hipótese razoável, não certificação.
- `vale_transporte.py` — **propositalmente não funcional**. Achado:
  ambos os arquivos têm só uma tabela de totalizadores por centro de
  custo/departamento nas colunas O/P — **zero registros reais de
  funcionário**. Também não há confirmação de qual coluna (`TOTAL`,
  `DESCONTO`, `ACRÉSCIMO`, `VALOR DA CARGA`) alimenta o evento 815. Fica
  `PENDENTE`.

**4) Achado novo: eventos da Matriz sem código confirmado.** A Matriz
real tem abas com dados reais de Vale-refeição (233 registros, após
filtrar artefato — ver item 5), Vale-compras, Convênio Farmácia e
Adicional Noturno — mas `config/clientes/art_latex.json` só cataloga os
eventos 50 e 1524 para a Matriz. **Não assumi que os códigos da Filial
(1955, 813, 806, 96) valem também para a Matriz** — isso ficaria
inventando uma regra de negócio não confirmada. Extração estrutural
funciona; construção de lançamento canônico para esses eventos na Matriz
fica corretamente marcada `invalido` (evento não cadastrado), não como
erro de dado.

**5) Achado de qualidade de dado (não é bug do extrator).** A aba
`Vale-refeicao` da Filial tem, a partir da linha ~239, um bloco de 762
linhas com valor `#REF!` (referência de fórmula quebrada) numa coluna
não usada (H), sem relação com os registros reais de funcionário
(colunas A-C). O extrator já ignora isso corretamente por não olhar essa
coluna — mas fica registrado como peculiaridade estrutural da planilha
real.

**Validação real agregada** (só em memória, nenhum dado individual
persistido):

| Evento | Unidade(s) | Total | Encontrados | Não enc. | Ambíguos | Status |
|---|---|---|---|---|---|---|
| 1955 VR | Filial | 233 | 190 | 43 | 0 | BLOCKED |
| 813 Compras | Filial | 21 | 16 | 5 | 0 | BLOCKED |
| 806 Farmácia | Filial | 7 | 5 | 2 | 0 | BLOCKED |
| 96 Ad. Noturno | Filial | 44 | 33 | 11 | 0 | BLOCKED |
| 1524 Cesta | Matriz+Filial | 317 (117+200) | 304 | 13 | 0 | BLOCKED |

Todos `BLOCKED` pela política fail-closed já adotada — nenhum tem 0 não
encontrados. Nenhum nome, CPF ou valor individual foi reproduzido; as
somas financeiras agregadas por evento (não identificam ninguém) foram
conferidas apenas em memória.

**Evidência:** execução real dos extratores contra os arquivos já em
`homologacao/art_latex/questor/origem/` e o cadastro real.
**Impacto:** `src/jrdp/minutos.py`,
`src/jrdp/extratores/{valor_simples,cesta_basica,horas,vale_transporte}.py`
(novos), `src/jrdp/conferencia.py` (duplicidades, total_horas_minutos,
reconciliar_total_fonte), `tests/test_minutos.py`,
`tests/test_extratores.py`, `tests/test_conferencia.py` (novos). Nenhuma
mudança em `config/clientes/art_latex.json` (o achado do item 4 não gerou
alteração de config — só ficou registrado como PENDENTE). Nenhum
exportador foi ligado à produção; `QuestorExporterH` continua bloqueando
incondicionalmente.

## 2026-09-17 — Correção: Decimal, não float; e camada canônica do pipeline (sem liberar produção)

**Contexto:** revisão crítica da entrada anterior (logo abaixo). O
usuário apontou corretamente que "sem arredondamento" não pode significar
serializar `float` bruto do Python/Excel — `Decimal(19.1)` produz
`Decimal('19.100000000000001421085471520200371742248535156250')`, um
artefato binário que a evidência do CSV real nunca mostrou. A evidência
observada (ausência de padding/arredondamento fixo) não autoriza
extrapolar para "aceita lixo de ponto flutuante".

**Decisão sobre decimais:** o motor deve usar `Decimal`, nunca `float`,
para valores tipo V. Regra travada em código e teste: nunca construir
`Decimal` a partir de `float` diretamente (sempre via `str(float)`
primeiro); nunca `round()`/`quantize()` para forçar casas. Implementado
em `src/jrdp/decimais.py` (`valor_origem_para_decimal`,
`serializar_decimal_livre`), com teste explícito provando que o
contra-exemplo clássico (`Decimal(19.1)` vs `Decimal(str(19.1))`) não
vaza para o resultado final (`tests/test_decimais.py`, 16 testes).
Achado adicional, também evidência-based: valores inteiros (`0`, `75`)
saem sem separador decimal no arquivo real — isso virou regra de
serialização (não é invenção; é o que os 33+13 casos observados mostram).

**Decisão sobre avançar sem o tipo H certificado:** construída a camada
canônica do pipeline (extração→normalização→matching→mapeamento de
evento→combinação Matriz+Filial→validação→relatório de conferência),
**sem liberar exportação de produção** para nenhum tipo, e mantendo tipo
H explicitamente `BLOCKED` por design (`QuestorExporterH` sempre levanta
erro, incondicionalmente). Isso permite avançar ~80-90% da automação sem
fingir que o contrato H está certificado.

**Novos módulos:** `src/jrdp/canonico.py` (`LancamentoCanonico`,
`RegistroOrigemBruto`, `agrupar_por_evento`), `src/jrdp/pipeline.py`
(`construir_lancamentos_evento`, `construir_lancamentos_cesta_basica`),
`src/jrdp/conferencia.py` (`RelatorioEvento`, `gerar_relatorio_evento`),
`src/jrdp/exportadores.py` (`QuestorExporterV`, `QuestorExporterH`,
`ExportacaoBlockedError`). 17 novos testes em `tests/test_pipeline.py`,
cobrindo: matching 100%, não encontrado, ambíguo, evento PENDENTE, evento
desconhecido, valor bruto inválido, rastreabilidade origem→canônico,
Cesta Básica Matriz+Filial combinadas em um conjunto por evento,
relatório PASS/BLOCKED, exportador V bloqueado por matching incompleto,
exportador H sempre bloqueado.

**Validação contra dados reais** (só em memória, nenhum dado persistido):
Cesta Básica da Matriz (117 nomes reais) → relatório `BLOCKED`, 114
encontrados, 3 não encontrados, 0 ambíguos, `pode_exportar() == False`;
`QuestorExporterV` recusou exportar, exatamente como projetado — fail-closed
mesmo com 114 de 117 resolvidos.

**Evidência:** reanálise do `evento_1889` para a regra de zero/inteiro
sem separador; execução real do pipeline contra `base_ativos_art_latex.csv`
e `planilha_importacao_matriz.xlsm` (já em
`homologacao/art_latex/questor/origem/`).
**Impacto:** `src/jrdp/decimais.py`, `src/jrdp/canonico.py`,
`src/jrdp/pipeline.py`, `src/jrdp/conferencia.py`,
`src/jrdp/exportadores.py` (todos novos), `tests/test_decimais.py`,
`tests/test_pipeline.py` (novos). `QuestorExporterV` não foi ligado a
`GERAR_PARA_O_QUESTOR.bat`/CLI — é só uma função de biblioteca testável,
não uma liberação de produção. `BLOCKED` global do P01 não foi removido.

## 2026-09-17 — Contrato físico do serializer (V), certificação H (PENDENTE), versão (PENDENTE), política fail-closed

> **Ver correção na entrada acima** (mesma data): a proposta original de
> "escrever a precisão que a conta produzir" foi refinada para "usar
> Decimal, nunca float" antes de qualquer implementação.

**Contexto:** antes de implementar o pipeline origem→Questor, o usuário
pediu para fechar o contrato físico do serializer, para não construir a
camada de negócio em cima de uma hipótese que pudesse exigir retrabalho.

**1) Precisão decimal de valores tipo V — caracterização refinada.**
Reanálise byte a byte do arquivo real `evento_1889` (182 registros):
distribuição de casas decimais `{0: 46, 1: 11, 2: 49, 3: 2, 4: 6, 5: 68}`;
nenhum valor negativo; nenhum separador `.`; zero sempre representado como
`"0"` isolado (nunca `"0,00"`); nenhum caso de casas decimais > 1
terminando em `0` foi encontrado na amostra (não é prova de que o Questor
"removeria" um zero à direita se existisse — é só ausência de
contra-exemplo nesta amostra). **Caracterização proposta**: o padrão
observado é mais bem descrito como **"nenhum arredondamento é aplicado —
o valor bruto de um cálculo é gravado como está"**, não como um "formato
de N casas variável". Isso muda a implicação para o gerador: a
responsabilidade de não arredondar é do **cálculo** que produz o valor,
não de uma regra de formatação de string. `src/jrdp/serializers.serialize_valor`
continua divergente (força 2 casas fixas) — **não alterado ainda**, essa
mudança fica para quando o gerador for implementado, com teste de
contrato antes da mudança.

**2) Certificação binária de um CSV real tipo H — NÃO REALIZADA.** Não
existe, no acervo de evidência atual, nenhum arquivo `.csv` físico com
`tipo=H` aceito pelo Questor — só o `evento_1889` (tipo V). **Não fabricar
nem inferir** essa estrutura a partir do tipo V. Fica `PENDENTE`
explicitamente até o usuário fornecer um arquivo real desse tipo. A regra
de negócio (H,MM, ex. `07:31` → `7,31`) continua confirmada
separadamente (ver entrada anterior) — o que falta é só a certificação
binária do arquivo, não a regra de valor.

**3) Versão do Questor/importador — PENDENTE, sem evidência.** Inspeção
dos metadados OOXML (`docProps/app.xml`, `docProps/core.xml`) dos dois
`.xlsm` reais mostra só metadados do Excel (não do Questor). Inspeção de
strings dentro de `xl/vbaProject.bin` encontrou a macro `GerarLayoutImportacao`
(módulo `Módulo3`) e a mensagem `"Conversao para o Questor concluida."`,
mas nenhuma versão numérica do Questor ou do importador. Fica `PENDENTE`
— nenhum artefato disponível permite confirmar isso sem inventar.

**4) Política fail-closed para matching — adotada e travada por testes
permanentes.** Nenhum arquivo de produção é gerado se houver qualquer
nome ambíguo OU não encontrado no cruzamento origem×cadastro — mesmo que
seja só 1 de 117. O relatório de conferência (`RelatorioConferencia`,
`avaliar_gate_matching`) sempre pode ser produzido, com status
`PASS`/`BLOCKED` e contagens, para o analista corrigir a origem/cadastro;
é a geração do arquivo de produção que fica proibida enquanto
`pode_gerar_arquivo_producao` for `False`. Implementado em
`src/jrdp/origem_matching.py`, travado por 6 novos testes em
`tests/test_origem_matching.py` (14 no total no módulo).

**Evidência:** arquivo real `evento_1889` (reanálise), metadados e
`vbaProject.bin` dos dois `.xlsm` reais já em
`homologacao/art_latex/questor/origem/`. Nenhum dado pessoal foi
reproduzido.
**Impacto:** `src/jrdp/origem_matching.py` (novo: `RelatorioConferencia`,
`avaliar_gate_matching`), `tests/test_origem_matching.py`. Nenhuma
mudança em `serializers.py` ainda. Pipeline origem→Questor continua não
implementado — depende de: item 2 (arquivo tipo H real) e decisão
explícita sobre a mudança de `serialize_valor`/cálculo antes de
implementar.

## 2026-09-17 — Cinco pendências do P01 resolvidas pelo usuário

**Contexto:** cinco pontos em aberto listados ao usuário após a
certificação de layout e a inventariação das planilhas de origem.
**Decisões:**

1. **Cesta Básica da Matriz — código confirmado.** O usuário confirmou:
   "o evento é desconto e o número do evento é 1524" — mesmo código do
   evento equivalente na Filial. `config/clientes/art_latex.json` e
   `.claude/rules/art-latex.md` atualizados; a regra de R$1,00/colaborador
   foi herdada por analogia com a Filial (não reconfirmada
   explicitamente para a Matriz — fica registrado como tal).
2. **Identidade do arquivo "Filial" — esclarecida, não é erro.** O
   usuário confirmou: "é só a planilha, a intenção é juntar os dois em um
   único arquivo pra importar no Questor". Isso implica que o pipeline de
   geração deve produzir **um único arquivo por evento**, combinando
   registros de Matriz e Filial, não dois arquivos separados.
3. **Eventos tipo H seguem a mesma regra H,MM.** Confirmado com exemplo:
   "07:31 de 50%, na conversão tem que ser 7,31". `serialize_hmm("07:31")`
   já produz `"7,31"` sem qualquer alteração de código — validado e
   travado por novo caso em
   `tests/test_serializers.py::test_serialize_hmm_casos_confirmados`.
   Certificação física binária de um arquivo `.csv` real com `tipo=H`
   continua não realizada (esta é uma confirmação de regra de negócio,
   não evidência binária).
4. **Cruzamento origem × cadastro implementado.** Novo módulo
   `src/jrdp/origem_matching.py`: cruza nomes das planilhas Matriz/Filial
   contra o cadastro de ativos (`cadastro_ativos.py`) por nome exato
   (normalizado por espaço/caixa). Nomes ambíguos (duplicados no
   cadastro) ou não encontrados **nunca são resolvidos automaticamente**
   — ficam explícitos em `ambiguos`/`nao_encontrados`, com
   `assert_sem_bloqueios` levantando `MatchingBlockedError` listando cada
   caso individualmente (nunca um resumo agregado), conforme
   `.claude/rules/matching.md`. Testado com 9 casos usando dados
   fictícios (`tests/test_origem_matching.py`).
**Evidência:** confirmações explícitas do usuário nesta sessão (2026-09-17).
Módulo de cruzamento validado também em memória contra dados reais (aba
"Cesta basica" da Matriz × cadastro real): 117 nomes, 114 resolvidos, 0
ambíguos, 3 não encontrados — números agregados apenas, nenhum nome
reproduzido em qualquer arquivo do repositório.
**Impacto:** `config/clientes/art_latex.json`, `.claude/rules/art-latex.md`,
`tests/test_config.py`, `tests/test_art_latex.py`,
`tests/test_serializers.py`, novo `src/jrdp/origem_matching.py` e
`tests/test_origem_matching.py`. O gerador ART LATEX → Questor completo
(que usaria esse cruzamento para montar o arquivo final) ainda não foi
implementado — falta decidir o que fazer com os 3 nomes não encontrados
antes de qualquer geração de produção real.

## 2026-09-17 — Chave de matching resolvida: "Contrato" == "COD. FUNC. QUESTOR"

**Contexto:** a entrada anterior (mesma data, logo abaixo) registrava a
ausência de código de funcionário nas planilhas reais Matriz/Filial como
bloqueio de matching. O usuário forneceu um relatório real ("Base de
ativos") extraído do sistema de origem, com colunas Contrato, Nome,
Admissão, Descrição (cargo) e CPF — 495 registros, `Contrato` e `CPF`
únicos e sem duplicata.
**Decisão:** perguntado explicitamente, o usuário **confirmou** que o
campo `Contrato` desse relatório é o mesmo código usado como `COD. FUNC.
QUESTOR` nas planilhas Matriz/Filial. Isso é uma confirmação do cliente
sobre um processo de negócio (não uma evidência física autoexplicativa,
já que a aba `Configuracoes` das planilhas Matriz/Filial estava vazia e
não permitia cruzar isso sozinha) — registrado como tal, no mesmo nível de
confiança de outras confirmações do cliente (ex.: formato H,MM). Isso
**desbloqueia** o uso de `Contrato`/CPF como chave de matching nome→código
via este cadastro, resolvendo o conflito com `.claude/rules/matching.md`.
**Evidência:** arquivo `.csv` real ("Base de ativos"), SHA-256
`74c35532b88350be10a7a7a8e121230bfa1aa44beb5c5a41632b9cf5032653c3`, 47156
bytes, mais a confirmação explícita do usuário em 2026-09-17. Nenhum nome,
CPF ou contrato real foi reproduzido em qualquer arquivo do repositório.
**Impacto:** novo módulo `src/jrdp/cadastro_ativos.py` (parser do relatório
paginado, com validação de contagem contra o próprio rodapé do arquivo, e
funções de indexação por contrato/CPF), `tests/test_cadastro_ativos.py`
(11 testes, fixture 100% sanitizada). Validado também em memória contra o
arquivo real (495/495 registros, contagem batendo com o rodapé). Ainda não
implementado: o cruzamento efetivo nome/CPF → contrato dentro do fluxo
origem (Matriz/Filial) → Questor — isso fica para quando o mapeamento for
implementado (outras pendências do P01 continuam abertas, ver
`docs/P01_ART_LATEX_QUESTOR.md`).

## 2026-09-17 — Chave de matching ausente nas planilhas reais ART LATEX (BLOCKED)

> **Bloqueio resolvido pela entrada acima** (mesma data). Mantida aqui por
> rastreabilidade de como o problema foi identificado antes de ser
> resolvido.

**Contexto:** inventário estrutural das planilhas reais de origem (Matriz e
Filial, `.xlsm`) para o P01, próximo passo após o gate de layout do
Questor.
**Decisão:** a coluna `COD. FUNC.` está vazia em 100% dos registros reais,
em todas as abas com dado, em ambos os arquivos. A única identificação
presente é nome livre. Por `.claude/rules/matching.md`, isso **bloqueia**
qualquer implementação de mapeamento origem→Questor até existir uma chave
confiável — não será implementado matching por nome. Três hipóteses
levantadas (cadastro mestre externo, matching feito pela macro VBA
embutida, preenchimento manual pela equipe de DP) não foram confirmadas;
pendente de resposta do usuário.
**Evidência:** dois arquivos `.xlsm` reais fornecidos pelo usuário em
2026-09-17 (Matriz: SHA-256
`11434b9ab14a16e88652d0a6bbaa5f6d270eb520e15f766d3ed628b3cb61904f`; Filial:
SHA-256 `5e0b918b8803f32769a1f0e48d20c3dc243d78f94d0eb7a3415e48784c57727e`),
inventariados com `openpyxl` em modo leitura. Nenhum nome, CPF, código de
funcionário ou valor individual foi reproduzido em qualquer arquivo do
repositório — apenas contagens agregadas.
**Impacto:** `docs/P01_ART_LATEX_QUESTOR.md` (seção "Planilhas de origem
ART LATEX — achados"), `homologacao/art_latex/questor/evidencia/manifest.json`.
Nenhum código de mapeamento foi escrito.

## 2026-09-17 — Coluna da Cesta Básica da Matriz: evidência contradiz registro anterior

**Contexto:** a entrada de 2026-09-16 (ver mais abaixo) registrava a Cesta
Básica da Matriz como associada à "coluna E `Desconto`".
**Decisão:** a evidência física (planilha real `Cesta basica` da Matriz)
mostra que a coluna E tem cabeçalho `CR`, não `Desconto`; não existe coluna
`Desconto` nesta aba. **Evidência física prevalece** sobre o registro
anterior, que era baseado em consolidação de memória, não em arquivo. O
código do evento da Cesta Básica da Matriz continua **PENDENTE** — esta
correção é só sobre qual coluna de origem, não resolve o código do evento
em si.
**Evidência:** arquivo `.xlsm` real da Matriz (ver decisão acima para
hash).
**Impacto:** `docs/P01_ART_LATEX_QUESTOR.md`. `config/clientes/art_latex.json`
mantém `"coluna_origem": "E", "coluna_origem_nome": "Desconto"` por
enquanto — **não corrigido silenciosamente**; precisa de decisão explícita
do usuário sobre se essa referência deve ser removida/atualizada.

## 2026-09-17 — Divergência de identidade do arquivo "Filial" (não resolvida)

**Contexto:** inventário do arquivo `.xlsm` recebido como "planilha de
importação Filial".
**Decisão:** registrado, não resolvido — o cabeçalho interno de várias
abas desse arquivo (incluindo `Configuracoes`) contém o texto "ART LATEX
IND E COM DE ARTEF DE LATEX- MATRIZ", igual ao do arquivo da Matriz. Não
presumido erro de template nem dados trocados; fica como pendência de
confirmação com o usuário.
**Evidência:** arquivo `.xlsm` real da Filial (ver hash na decisão sobre
matching acima).
**Impacto:** `docs/P01_ART_LATEX_QUESTOR.md`.

## 2026-09-17 — Certificação física do layout genérico do Questor (gate: PASS)

**Contexto:** substituição da evidência por print (CONDICIONAL, entrada
anterior) por análise binária de um arquivo `.csv` real, informado como já
aceito/importado com sucesso pelo Questor.
**Decisão:** contrato físico **CONFIRMADO POR EVIDÊNCIA FÍSICA**: encoding
CP850 (não Latin-1/UTF-8), delimitador `;`, terminador CRLF, sem BOM, sem
aspas, linha 1 = `;;;<código do evento>`, linha 2 = `;;;<tipo>`, linha 3 =
cabeçalho exato `CÓDGIO;NOME;;` (erro de digitação faz parte do contrato),
linha 4+ = `<código>;<nome>;;<valor>` com coluna C sempre vazia. Valor sem
precisão decimal fixa (0 a 5 casas no mesmo arquivo). Gate de certificação
estrutural: **PASS**. Isso NÃO substitui nem confirma nenhuma regra de
negócio da ART LATEX (eventos, Matriz/Filial, H,MM) — é só o contrato do
sistema Questor, camada separada por design (ver
`.claude/rules/governanca.md`).
**Conflito identificado e não resolvido silenciosamente:**
`src/jrdp/serializers.serialize_valor` assume 2 casas decimais fixas; a
evidência física mostra precisão variável sem padding. A evidência física
prevalece sobre a suposição anterior, mas a mudança de código só será
aplicada quando o gerador ART LATEX → Questor for implementado (fora de
escopo desta fase) — ver `docs/P01_ART_LATEX_QUESTOR.md`.
**Evidência:** arquivo `.csv` real (nome do cliente de origem do arquivo:
Nova Farma, usado como referência genérica de layout), SHA-256
`ec55b1904002719b36bf08e544472080cba76f9fbc67e57855f6389337ea01da`, 11382
bytes, analisado byte a byte com Python em 2026-09-17. Nenhum dado do
arquivo (nomes, códigos de funcionário, valores) foi reproduzido em
qualquer arquivo versionado.
**Impacto:** `src/jrdp/questor_layout.py` (novo — parser do contrato, nunca
reformata o valor), `tests/test_questor_layout.py` (12 testes, fixture
sanitizada), `homologacao/art_latex/questor/evidencia/manifest.json`,
`docs/P01_ART_LATEX_QUESTOR.md`. Nenhuma mudança em
`config/clientes/art_latex.json` ou nas regras de negócio da ART LATEX.

## 2026-09-17 — Estrutura do layout genérico de importação do Questor (CONDICIONAL)

> **Superada pela certificação física acima** (mesma data). Mantida aqui
> por rastreabilidade histórica de como a evidência evoluiu de print para
> arquivo físico.

**Contexto:** homologação física do layout de importação do Questor para o
P01 (ver `docs/P01_ART_LATEX_QUESTOR.md`).
**Decisão:** confirmada estruturalmente (por print de tela, não pelo
arquivo físico) a estrutura de um arquivo CSV (MS-DOS) de importação,
válida para qualquer cliente/evento, um arquivo por evento: linha 1/coluna
D = código do evento; linha 2/coluna D = tipo (`V`=Valor observado; `H`
seria o equivalente para Hora); linha 3 = cabeçalho `CÓDIGO`/`NOME`; linha
4+ = dados por funcionário. Classificação: **CONDICIONAL** — delimitador,
encoding e precisão decimal real ainda não confirmados, pois só um print
foi recebido, não o arquivo físico. Nenhum dado do print (nomes, valores,
códigos de funcionário) foi reproduzido em qualquer arquivo do repositório.
**Evidência:** print de tela fornecido pelo usuário em 2026-09-17,
descrito como arquivo já aceito/importado com sucesso no Questor.
**Impacto:** `docs/P01_ART_LATEX_QUESTOR.md` (seção "Layout do importador
do Questor — achados"). Nenhuma mudança em `config/clientes/art_latex.json`
ou `src/jrdp/serializers.py` — a divergência observada na precisão decimal
dos valores não deve ser incorporada ao código sem o arquivo físico.

## 2026-09-16 — Regras de eventos ART LATEX (Filial e Matriz)

**Contexto:** definição dos códigos de evento usados na importação de
variáveis/benefícios do ART LATEX para o Questor.
**Decisão:** códigos confirmados conforme `config/clientes/art_latex.json`
(Filial: 35, 49, 23, 29, 25, 1955, 815, 1524, 806, 813, 96; Matriz: 50). O
código da Cesta Básica da Matriz (coluna E "Desconto") fica PENDENTE — sem
evidência suficiente para definição.
**Evidência:** consolidação fornecida pelo usuário na sessão de estruturação
do projeto.
**Impacto:** `config/clientes/art_latex.json`, `.claude/rules/art-latex.md`.

## 2026-09-16 — Formato de hora H,MM travado por teste

**Contexto:** risco de uma futura alteração de código transformar a regra
do importador (H,MM) em hora decimal matemática.
**Decisão:** `01:30` deve sempre serializar para `1,30`, nunca `1,50`.
**Evidência:** confirmação explícita do usuário com exemplos (00:32→0,32,
01:52→1,52, 04:07→4,07, 06:00→6,00).
**Impacto:** `src/jrdp/serializers.py`,
`tests/test_serializers.py::test_hmm_never_converts_to_decimal_hours`.

## Erros históricos

### Evento 1603 (07/2026) — ART LATEX

Foi um erro histórico e não deve ser reaproveitado como referência de
código de evento em nenhuma automação futura. Bloqueado em
`config/clientes/art_latex.json` (`erros_historicos`) e coberto por
`tests/test_art_latex.py::test_bloqueia_evento_1603_como_erro_historico`.
