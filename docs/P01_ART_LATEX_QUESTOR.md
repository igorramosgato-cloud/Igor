# P01 — Variáveis + Benefícios ART LATEX → Questor

## Status: BLOCKED para geração de produção (camada canônica do pipeline construída e testada; tipo H e versão do Questor: PENDENTES por falta de evidência; nenhum exportador ligado à produção)

Regras de negócio já parametrizadas (`config/clientes/art_latex.json`,
`.claude/rules/art-latex.md`) e cobertas por testes (`tests/test_art_latex.py`,
`tests/test_config.py`, `tests/test_serializers.py`).

O **contrato físico do layout genérico de importação do Questor** foi
certificado em 2026-09-17 (gate: PASS) a partir de um arquivo real — ver
seção abaixo. Isso é uma camada diferente da regra de negócio da ART LATEX
(eventos, Matriz/Filial, H,MM), que continua parametrizada
separadamente e ainda tem pendências próprias (ver "Pendências").

## Layout do importador do Questor — certificação física (2026-09-17)

Evidência: arquivo físico real (`.csv`), analisado em nível de bytes com
Python (não Excel/pandas), descrito pelo usuário como já aceito/importado
com sucesso pelo Questor. É um layout **genérico**, reutilizável por
qualquer cliente/evento — este exemplo específico veio de outro cliente
("Nova Farma"), usado aqui apenas como evidência de contrato de sistema, não
de regra de negócio da ART LATEX. Nenhum dado do arquivo (nomes, códigos de
funcionário, valores) foi reproduzido em qualquer local versionado — ver
`.claude/rules/homologacao-dados.md`. Hash e metadados em
`homologacao/art_latex/questor/evidencia/manifest.json`.

Implementado em `src/jrdp/questor_layout.py`, testado em
`tests/test_questor_layout.py` com fixture 100% sanitizada
(`tests/fixtures/questor/layout_generico_sanitizado.csv`), e validado em
memória contra o arquivo físico real (182/182 registros extraídos
corretamente, sem persistir nenhum dado).

### CONFIRMADO POR EVIDÊNCIA FÍSICA

- **Encoding: CP850** (confirmado byte a byte — o byte `0xE0` decodifica
  como `Ó` em CP850, batendo com o cabeçalho real `CÓDGIO`; em Latin-1
  daria `à`, incorreto). Não usar Latin-1/UTF-8.
- **Terminador de linha: CRLF** — 100% das quebras no arquivo real.
- **Delimitador: `;`** — 100% das 1000 linhas físicas com 4 colunas.
- **Sem BOM. Sem aspas** em nenhum lugar do arquivo.
- Linha 1: `;;;<código do evento>` (ex.: `1889` no arquivo de evidência).
- Linha 2: `;;;<tipo>` (`V` observado; `H` seria o equivalente por extensão
  para eventos de hora, não observado diretamente ainda).
- Linha 3: cabeçalho **exato** `CÓDGIO;NOME;;` — o "erro de digitação"
  (`CÓDGIO`, não `CÓDIGO`) é parte real do contrato, não deve ser corrigido
  ao gerar o arquivo.
- Linha 4 em diante: `<código>;<nome>;;<valor>` — coluna C sempre vazia
  (confirmado nas 182 linhas de dados do arquivo real).
- Registros terminam na primeira linha `;;;`; o restante pode ser
  preenchido com linhas `;;;` de padding (no arquivo de evidência, até
  completar exatamente 1000 linhas físicas — contagem exata de padding não
  confirmada como requisito, apenas observada nesse arquivo).
- **Coluna de valor sem precisão decimal fixa nem zero-padding** — o
  arquivo real tem valores com 0 a 5 casas decimais no mesmo arquivo
  (`382,18378`, `4,11`, `99,4`, `75`, `0`), sem sinal negativo e sem
  espaços.

### Precisão decimal de valores tipo V — caracterização refinada (2026-09-17)

- Reanálise byte a byte dos 182 registros do `evento_1889`: distribuição
  de casas decimais `{0: 46, 1: 11, 2: 49, 3: 2, 4: 6, 5: 68}`; nenhum
  valor negativo; nenhum separador `.`; zero sempre `"0"` isolado (nunca
  `"0,00"`); nenhum caso de casas > 1 terminando em `0` na amostra (não
  prova que zero à direita seria removido se existisse — é ausência de
  contra-exemplo, não uma regra confirmada).
- **Caracterização proposta**: o padrão não é "um formato de N casas
  variável" — é mais bem descrito como **"nenhum arredondamento é
  aplicado; o valor bruto do cálculo é gravado como está"**.
- **Correção crítica (2026-09-17, mesmo dia)**: "sem arredondamento" NÃO
  autoriza serializar `float` bruto do Python/Excel. `Decimal(19.1)`
  produz um artefato binário de 50+ dígitos que a evidência nunca
  mostrou. Implementado `src/jrdp/decimais.py`: o motor usa `Decimal`
  (nunca `float` direto — sempre via `str(float)` primeiro), sem
  `round()`/`quantize()`. Valores inteiros saem sem separador decimal
  (`0`, `75`), conforme evidência real. 16 testes em
  `tests/test_decimais.py`, incluindo o contra-exemplo clássico
  `Decimal(19.1)` vs `Decimal(str(19.1))`.
- `src/jrdp/serializers.serialize_valor` (o antigo, com 2 casas fixas)
  continua existindo mas foi **substituído** por
  `decimais.serializar_decimal_livre` na camada canônica do pipeline
  (`src/jrdp/pipeline.py`) — é este último que reflete a evidência real.
- `src/jrdp/questor_layout.py` já refletia a evidência desde antes: nunca
  reformata o valor, devolve a string bruta como está no arquivo.

### Eventos tipo H (Hora) — regra de negócio confirmada; certificação binária PENDENTE (2026-09-17)

- O usuário confirmou que o mesmo formato H,MM já implementado vale para
  eventos tipo `H`: exemplo dado, `07:31` de HE 50% deve virar `7,31`.
  `serialize_hmm("07:31")` já produz exatamente isso, sem alteração de
  código — travado em
  `tests/test_serializers.py::test_serialize_hmm_casos_confirmados`.
- **Certificação binária NÃO realizada**: não existe, no acervo de
  evidência atual, nenhum arquivo `.csv` físico com `tipo=H` aceito pelo
  Questor — só o `evento_1889` (tipo V). Não foi fabricada nem inferida
  essa estrutura a partir do tipo V. Isso fica genuinamente **PENDENTE**
  até o usuário fornecer um arquivo real desse tipo.

### Versão do Questor/importador — PENDENTE, sem evidência disponível (2026-09-17)

- Inspecionados os metadados OOXML (`docProps/app.xml`, `docProps/core.xml`)
  dos dois `.xlsm` reais — só revelam metadados do Microsoft Excel, não do
  Questor.
- Inspecionadas strings dentro de `xl/vbaProject.bin` (Matriz): encontrada
  a macro `GerarLayoutImportacao` (módulo `Módulo3`) e a mensagem
  `"Conversao para o Questor concluida."`, mas nenhuma versão numérica do
  Questor ou do importador.
- Fica **PENDENTE** — nenhum artefato disponível permite confirmar isso
  sem inventar.

### CONDICIONAL / PENDENTE

- Certificação binária de um arquivo `.csv` real com `tipo=H` — ver acima.
- Versão específica do Questor/layout do conversor — ver acima.

## Planilhas de origem ART LATEX — achados (2026-09-17)

Evidência: dois arquivos `.xlsm` reais (macro-habilitados), um para Matriz
e um para Filial, inventariados com `openpyxl` em modo leitura. **Nenhum
nome, CPF, código de funcionário ou valor individual foi reproduzido em
qualquer arquivo do repositório** — apenas contagens agregadas e nomes de
colunas/abas. Ver `.claude/rules/homologacao-dados.md`. Hash e metadados
em `homologacao/art_latex/questor/evidencia/manifest.json`. Os arquivos
originais ficam só localmente em
`homologacao/art_latex/questor/origem/` (fora do Git).

### CONFIRMADO POR EVIDÊNCIA FÍSICA

- Ambos os arquivos usam a **mesma estrutura de abas** (mesmo template):
  `Importacoes`, `Configuracoes`, `Cesta basica`, `Plano de saude`,
  `Vale-transporte`, `Vale-refeicao`, `Vale-compras`, `convenio farmacia`,
  `Adicional Noturno`, `Hora-extra` (Filial tem ainda uma aba extra vazia
  `Plan1`).
- Cabeçalho de identificação em cada aba de benefício: `COD. FUNC.` |
  `NOME DO EMPREGADO` | colunas específicas do benefício.
- Aba `Configuracoes` tem cabeçalho `COD. FUNC. QUESTOR` | `NOME DO
  EMPREGADO` | `CENTRO DE CUSTO` | `DEPARTAMENTO` | `ESTABELECIMENTO` |
  flags "Tem cesta básica?" / "Tem plano de saúde?" / "Tem vale
  transporte?" / "Tem vale refeição?" / "Tem vale compras?" — seria a
  tabela mestre de cadastro, mas está **vazia** em ambos os arquivos
  recebidos (0 linhas de dado).
- Aba `Plano de saude` tem coluna **CPF** no cabeçalho (dado ainda mais
  sensível que nome — reforça a necessidade de nunca versionar este
  arquivo, já coberta por `.claude/rules/homologacao-dados.md`).
- Contagem de registros reais por aba (Matriz / Filial):
  `Cesta basica`: 117 / 200; `Vale-refeicao`: ≥924 / ≥995 (limite de
  varredura, pode haver mais); `Vale-compras`: 3 / 21; `convenio
  farmacia`: 4 / 7; `Adicional Noturno`: 72 / 44.
- `Plano de saude` e `Hora-extra`: **0 registros reais** em ambos os
  arquivos (só cabeçalho) — nenhuma evidência de formato de valor/hora
  disponível ainda para essas duas abas.
- Arquivos são macro-habilitados (`.xlsm`, contêm `xl/vbaProject.bin`) —
  a coluna "Ações" em cada aba sugere que um botão de macro processa os
  dados; a lógica de geração pode estar na macro, não só na planilha.

### CHAVE DE MATCHING — bloqueio identificado e depois RESOLVIDO (2026-09-17)

- A coluna `COD. FUNC.` existe no cabeçalho de **toda** aba com dado, mas
  estava **vazia em 100% dos registros reais**, em **ambos** os arquivos
  (Matriz e Filial), em todas as abas com dados. A única identificação
  presente na prática era o **nome livre** (`NOME DO EMPREGADO`), o que
  violaria `.claude/rules/matching.md`.
- **Resolvido**: o usuário forneceu um relatório real de cadastro ("Base
  de ativos", extraído do sistema de origem) com colunas `Contrato`
  (código), `Nome`, `Admissão`, `Descrição` (cargo) e `CPF` — 495
  registros, `Contrato` e `CPF` ambos únicos e sem duplicata — e
  **confirmou explicitamente** que `Contrato` é o mesmo código usado como
  `COD. FUNC. QUESTOR`. Ver `docs/DECISIONS.md` (2026-09-17).
- Implementado em `src/jrdp/cadastro_ativos.py` (parser do relatório
  paginado, valida a contagem extraída contra o rodapé do próprio
  arquivo), testado em `tests/test_cadastro_ativos.py` com fixture 100%
  sanitizada, e validado em memória contra o arquivo real (495/495
  registros). Isso dá as funções `indexar_por_contrato` e
  `indexar_por_cpf` para resolver nome/CPF → código de forma confiável.
- **Implementado (2026-09-17)**: `src/jrdp/origem_matching.py` faz o
  cruzamento nome→código entre as planilhas de origem e o cadastro,
  usando nome exato (normalizado por espaço/caixa). Nomes ambíguos
  (duplicados no cadastro) ou não encontrados **nunca são resolvidos
  automaticamente** — ficam explícitos em `ambiguos`/`nao_encontrados`, e
  `assert_sem_bloqueios` levanta `MatchingBlockedError` listando cada caso
  individualmente. Testado com dados fictícios em
  `tests/test_origem_matching.py`. Validado em memória contra dados reais
  (aba `Cesta basica` da Matriz × cadastro real): **117 nomes, 114
  resolvidos, 0 ambíguos, 3 não encontrados** (números agregados apenas —
  nenhum nome reproduzido em qualquer arquivo do repositório).
- **Política fail-closed adotada (2026-09-17)**: nenhum arquivo de
  produção é gerado se houver qualquer nome ambíguo OU não encontrado —
  mesmo que seja só 1 de 117. `avaliar_gate_matching` sempre produz um
  `RelatorioConferencia` (status `PASS`/`BLOCKED` + contagens), que pode
  ser gerado mesmo quando bloqueado, para o analista corrigir a
  origem/cadastro. Travado por 6 testes permanentes em
  `tests/test_origem_matching.py` (ex.:
  `test_gate_bloqueia_com_apenas_um_nao_encontrado`).
- **Ainda não implementado**: a montagem do arquivo final combinando
  Matriz+Filial (ver próxima seção) usando esse cruzamento, e o fluxo
  operacional de correção quando o gate fica `BLOCKED` (quem corrige o
  quê, onde).

### Cesta Básica da Matriz — código confirmado pelo usuário (2026-09-17)

- Decisão anterior (`docs/DECISIONS.md`, 2026-09-16) registrava a Cesta
  Básica da Matriz como vinculada à "coluna E `Desconto`" — **evidência
  física mostrou que isso estava errado** (a coluna E real é `CR`, não
  `Desconto`; não há coluna `Desconto` nesta aba).
- O usuário então confirmou diretamente: **"o evento é desconto e o
  número do evento é 1524"** — mesmo código do evento equivalente na
  Filial. `config/clientes/art_latex.json` e `.claude/rules/art-latex.md`
  atualizados; não é mais PENDENTE.
- Como a aba `Cesta basica` da Matriz não tem coluna de valor explícita
  (só `COD. FUNC.`, `NOME DO EMPREGADO`, `DEPARTAMENTO`, `CENTRO DE
  CUSTO`, `CR`, `Assinatura`), o valor é derivado por **contagem de
  colaboradores listados** (R$ 1,00 cada — regra herdada por analogia com
  a Filial, não reconfirmada explicitamente para a Matriz).

### Identidade do arquivo Filial — esclarecida (2026-09-17)

- O usuário confirmou: **"é só a planilha, a intenção é juntar os dois em
  um único arquivo pra importar no Questor"**. O cabeçalho interno
  dizendo "MATRIZ" no arquivo Filial é só resquício de template, não um
  erro nem dados trocados.
- **Implicação de arquitetura**: o pipeline de geração deve produzir **um
  único arquivo por evento**, combinando registros de Matriz e Filial —
  não dois arquivos separados. Isso ainda não foi implementado.

## Camada canônica do pipeline — construída e testada, produção NÃO liberada (2026-09-17)

Implementada a camada entre origem e exportação final, separando
rigorosamente regra de negócio, cálculo, validação e serialização física:

- `src/jrdp/canonico.py` — `LancamentoCanonico` (modelo interno com
  rastreabilidade completa: cliente, competência, unidade, código,
  evento, tipo, valores original/normalizado, arquivo/aba/linha de
  origem, regra aplicada, status de matching/validação) e
  `agrupar_por_evento`.
- `src/jrdp/pipeline.py` — `construir_lancamentos_evento` (matching +
  regra do evento + serialização) e `construir_lancamentos_cesta_basica`
  (Matriz+Filial combinadas, R$1,00/colaborador listado).
- `src/jrdp/conferencia.py` — `RelatorioEvento`/`gerar_relatorio_evento`:
  contagens por unidade, matching, validade, soma (só tipo valor), status
  PASS/BLOCKED. Sempre gerável, mesmo bloqueado.
- `src/jrdp/exportadores.py` — `QuestorExporterV` (só produz saída
  quando o relatório está PASS — fail-closed, nunca arquivo parcial) e
  `QuestorExporterH` (bloqueia **incondicionalmente**, independente do
  relatório — não existe arquivo `tipo=H` real para basear isso).

**Nenhum exportador foi ligado a `GERAR_PARA_O_QUESTOR.bat` ou à CLI** —
são funções de biblioteca testáveis, não uma liberação de produção. O
`BLOCKED` global do P01 continua valendo.

**Validação contra dados reais** (só em memória, nenhum dado persistido):
Cesta Básica da Matriz (117 nomes reais) processada pela pipeline
completa → `RelatorioEvento(status="BLOCKED", encontrados=114,
nao_encontrados=3, ambiguos=0)`, `pode_exportar() == False`;
`QuestorExporterV` recusou exportar. Fail-closed confirmado
funcionando mesmo com 114 de 117 resolvidos.

37 novos testes (`tests/test_decimais.py`: 16, `tests/test_pipeline.py`:
17, mais os 4 do `origem_matching.py` fail-closed), todos com dados
fictícios.

## Pendências para liberar a geração real

1. ~~Layout físico/binário do importador do Questor (tipo V)~~ —
   **CONFIRMADO** (gate PASS).
2. ~~Planilhas-fonte reais Matriz/Filial da ART LATEX~~ — **recebidas e
   inventariadas**.
3. ~~Chave de matching confiável~~ — **RESOLVIDA E IMPLEMENTADA**
   (`cadastro_ativos.py` + `origem_matching.py`).
4. ~~Código do evento da Cesta Básica da Matriz~~ — **CONFIRMADO** (1524).
5. **Regra de negócio para eventos tipo H** — CONFIRMADA PELO CLIENTE
   (mesma regra H,MM já implementada). **Certificação binária de um
   `.csv` real com `tipo=H` continua PENDENTE** — não existe esse
   arquivo no acervo de evidência ainda; precisa ser fornecido pelo
   usuário, não pode ser inferido do tipo V. `QuestorExporterH` bloqueia
   incondicionalmente até isso mudar.
6. ~~Identidade do arquivo Filial~~ — **ESCLARECIDA** (é intencional; o
   objetivo é um único arquivo combinado Matriz+Filial por evento, já
   implementado em `construir_lancamentos_cesta_basica`/`agrupar_por_evento`).
7. **Versão específica do Questor/layout do conversor** — PENDENTE, sem
   evidência disponível nos artefatos atuais (metadados dos `.xlsm` e
   strings do VBA não revelam isso).
8. ~~Política de matching (fail-closed)~~ — **ADOTADA E IMPLEMENTADA**
   (`avaliar_gate_matching` + `RelatorioEvento`, testes permanentes).
9. ~~Decisão sobre a serialização de valores tipo V~~ — **IMPLEMENTADA**
   com `Decimal` (nunca `float`), sem arredondamento artificial (ver
   `src/jrdp/decimais.py`).
10. ~~Camada canônica do pipeline~~ — **CONSTRUÍDA E TESTADA**
    (extração→normalização→matching→mapeamento de evento→combinação
    Matriz+Filial→validação→relatório). **Falta ainda**: a extração real
    das demais abas de benefício além de Cesta Básica (Vale-refeição,
    Vale-compras, convênio farmácia, Adicional Noturno, Hora-extra — essa
    última sem dados reais para validar), e a decisão operacional de
    quem/como corrige nomes não encontrados quando o gate fica BLOCKED.
11. **Liberar exportação de produção** — não liberado nesta fase. Falta:
    itens 5 e 7 acima, testes end-to-end completos, e decisão explícita
    de homologação (ver `.claude/skills/homologar-automacao/SKILL.md`).

Ver `.claude/skills/gerar-questor/SKILL.md` para o procedimento completo e
`docs/BACKLOG.md` para o próximo passo.
