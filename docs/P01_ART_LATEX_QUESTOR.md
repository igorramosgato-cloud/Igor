# P01 — Variáveis + Benefícios ART LATEX → Questor

## Status: BLOCKED para geração de produção (layout, matching, Cesta Matriz, tipo H e identidade Filial: RESOLVIDOS; falta implementar o pipeline)

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

### Eventos tipo H (Hora) — regra de serialização confirmada pelo cliente (2026-09-17)

O usuário confirmou que o mesmo formato H,MM já implementado vale para
eventos tipo `H`: exemplo dado, `07:31` de HE 50% deve virar `7,31`.
`serialize_hmm("07:31")` já produz exatamente isso, sem alteração de
código — travado em
`tests/test_serializers.py::test_serialize_hmm_casos_confirmados`. A
certificação **binária** de um arquivo `.csv` real com `tipo=H` (como foi
feita para `tipo=V`) continua não realizada — isso é confirmação de regra
de negócio, não evidência física direta do contrato de arquivo.

### CONDICIONAL / PENDENTE

- Certificação binária de um arquivo `.csv` real com `tipo=H` (a regra de
  valor já está confirmada pelo cliente, ver acima; falta só o arquivo
  físico para o mesmo nível de certificação que o tipo `V` recebeu).
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
- **Ainda não implementado**: o que fazer com os nomes não encontrados
  antes de gerar produção (ex.: reportar para o DP corrigir manualmente no
  cadastro ou na planilha de origem), e a montagem do arquivo final
  combinando Matriz+Filial (ver próxima seção) usando esse cruzamento.

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

## Pendências para liberar a geração real

1. ~~Layout físico/binário do importador do Questor (tipo V)~~ —
   **CONFIRMADO** (gate PASS).
2. ~~Planilhas-fonte reais Matriz/Filial da ART LATEX~~ — **recebidas e
   inventariadas**.
3. ~~Chave de matching confiável~~ — **RESOLVIDA E IMPLEMENTADA**
   (`cadastro_ativos.py` + `origem_matching.py`).
4. ~~Código do evento da Cesta Básica da Matriz~~ — **CONFIRMADO** (1524).
5. ~~Regra de serialização para eventos tipo H~~ — **CONFIRMADA PELO
   CLIENTE** (mesma regra H,MM já implementada). Falta só a certificação
   binária de um arquivo `.csv` real com `tipo=H`.
6. ~~Identidade do arquivo Filial~~ — **ESCLARECIDA** (é intencional; o
   objetivo é um único arquivo combinado Matriz+Filial por evento).
7. Versão específica do Questor/layout do conversor — ainda não
   confirmada.
8. **Implementar o pipeline de geração propriamente dito**: extrair os
   valores reais de cada aba de benefício (Matriz/Filial), resolver
   código via `origem_matching`, decidir o que fazer com nomes não
   encontrados, combinar Matriz+Filial em um único arquivo por evento no
   layout certificado, e decidir a precisão decimal real do valor (a
   evidência física mostra precisão variável sem padding — ver "Conflito
   registrado" na seção de layout). Isso ainda não foi escrito.

Ver `.claude/skills/gerar-questor/SKILL.md` para o procedimento completo e
`docs/BACKLOG.md` para o próximo passo.
