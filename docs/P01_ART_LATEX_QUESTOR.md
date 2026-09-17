# P01 — Variáveis + Benefícios ART LATEX → Questor

## Status: BLOCKED para geração de produção (gate de layout: PASS)

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

### CONFLITO REGISTRADO (não resolvido silenciosamente)

- `src/jrdp/serializers.serialize_valor` sempre formata com 2 casas
  decimais fixas. A evidência física mostra que o Questor aceita — e o
  arquivo real usa — precisão variável sem padding.
- **Evidência física prevalece sobre a suposição anterior** (2 casas
  fixas), porque foi validada por análise binária de um arquivo
  efetivamente aceito pelo Questor, não por inferência.
- **Proposta (não implementada ainda):** ao gerar o arquivo final para o
  Questor, o valor deveria ser escrito com a precisão que a conta
  realmente produzir, sem forçar 2 casas — mas isso só deve ser decidido
  quando o gerador ART LATEX → Questor for de fato implementado (fora de
  escopo desta fase, que é só a certificação do layout). Ver
  `docs/DECISIONS.md` (2026-09-17).
- `src/jrdp/questor_layout.py` já reflete a evidência: nunca reformata o
  valor, devolve a string bruta como está no arquivo.

### CONDICIONAL / PENDENTE

- Se o layout de eventos do tipo `H` (Hora) segue exatamente o mesmo
  contrato de encoding/delimitador — não observado diretamente ainda
  (só vimos um arquivo tipo `V`).
- Código do evento da Cesta Básica da Matriz (ver `.claude/rules/art-latex.md`)
  — continua PENDENTE, sem relação com este gate de layout.
- Versão específica do Questor/layout do conversor — não confirmada.

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

### CONFLITO CRÍTICO — chave de matching ausente (BLOQUEIA o próximo passo)

- A coluna `COD. FUNC.` existe no cabeçalho de **toda** aba com dado, mas
  está **vazia em 100% dos registros reais**, em **ambos** os arquivos
  (Matriz e Filial), em todas as abas com dados. A única identificação
  presente na prática é o **nome livre** (`NOME DO EMPREGADO`).
- Isso viola diretamente `.claude/rules/matching.md` ("nunca nome livre").
  Por essa regra, a tarefa de mapeamento origem → Questor fica
  **BLOCKED** até existir uma chave confiável — não vou implementar
  matching por nome, mesmo que pareça "dar certo" na maioria dos casos.
- **Hipóteses não confirmadas** (preciso de confirmação do usuário, não
  vou assumir nenhuma):
  1. Existe um cadastro mestre separado (fora destes dois arquivos) que
     preenche `Configuracoes` com código+nome antes da geração?
  2. A macro VBA embutida faz o de-para nome→código consultando outra
     fonte (ex.: exportação do Questor) no momento da geração?
  3. O preenchimento do código é manual, feito pela equipe de DP depois
     de exportar/antes de gerar o arquivo final?
- Enquanto isso não for esclarecido, nenhum código de mapeamento
  origem→Questor será implementado.

### CONFLITO REGISTRADO — coluna da Cesta Básica da Matriz

- Decisão anterior (`docs/DECISIONS.md`, 2026-09-16) registrava a Cesta
  Básica da Matriz como vinculada à "coluna E `Desconto`".
- Evidência física agora mostra que a aba `Cesta basica` da Matriz tem,
  na coluna E, o cabeçalho `CR` (Centro de... algo, não confirmado o que
  significa), **não** `Desconto`. Não há coluna `Desconto` nesta aba.
- **Evidência física prevalece** sobre o registro anterior (que era uma
  consolidação de memória, não um arquivo). O código do evento da Cesta
  Básica da Matriz continua **PENDENTE** — a correção aqui é só sobre
  qual coluna, não resolve o código do evento.

### CONFLITO REGISTRADO — identidade do arquivo Filial

- O arquivo recebido como "planilha de importação **Filial**" tem, na
  aba `Configuracoes` e em outras, o mesmo texto de cabeçalho `"ART LATEX
  IND E COM DE ARTEF DE LATEX- MATRIZ"` usado no arquivo da Matriz.
- Não vou assumir que isso é um erro de template inofensivo nem que os
  dados estão trocados — fica registrado como divergência a confirmar
  com o usuário.

### CONDICIONAL / PENDENTE (herdado da certificação do layout)

- Formato de hora/valor para `Hora-extra` e `Plano de saude` — sem
  evidência (0 registros reais nas duas abas, nos dois arquivos).
- Se o layout de eventos do tipo `H` (Hora) segue o mesmo contrato de
  encoding/delimitador do Questor — ainda não observado.
- Código do evento da Cesta Básica da Matriz — continua PENDENTE.
- Versão específica do Questor/layout do conversor — não confirmada.

## Pendências para liberar a geração real

1. ~~Layout físico/binário do importador do Questor~~ — **CONFIRMADO**
   (gate PASS). Resta confirmar o comportamento para eventos tipo `H`.
2. ~~Planilhas-fonte reais Matriz/Filial da ART LATEX~~ — **recebidas e
   inventariadas**, mas revelaram um bloqueio novo (ver "Conflito
   crítico" acima).
3. **Chave de matching confiável** (código de funcionário) — **ausente**
   nos dados reais recebidos. Bloqueia qualquer mapeamento origem→Questor
   até esclarecido.
4. Código do evento da Cesta Básica da Matriz.
5. Versão específica do Questor/layout do conversor.
6. Decisão explícita sobre a precisão decimal do valor ao implementar o
   gerador (ver seção de layout, "Conflito registrado").
7. Esclarecer a divergência de identidade do arquivo Filial (cabeçalho
   diz "MATRIZ").

Ver `.claude/skills/gerar-questor/SKILL.md` para o procedimento completo e
`docs/BACKLOG.md` para o próximo passo.
