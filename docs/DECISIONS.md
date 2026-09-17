# Decisões

Entradas mais recentes no topo. Formato definido em
`.claude/skills/registrar-decisao/SKILL.md`.

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
