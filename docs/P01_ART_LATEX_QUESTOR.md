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

## Pendências para liberar a geração real

1. ~~Layout físico/binário do importador do Questor~~ — **CONFIRMADO**
   (gate PASS, ver seção acima). Resta confirmar o comportamento para
   eventos tipo `H`.
2. Planilhas-fonte reais Matriz/Filial da ART LATEX (abas e cabeçalhos).
3. Chave usada para identificar o funcionário nas planilhas de origem da
   ART LATEX, e se ela bate com a coluna "CÓDIGO" do layout Questor.
4. Código do evento da Cesta Básica da Matriz.
5. Versão específica do Questor/layout do conversor.
6. Decisão explícita sobre a precisão decimal do valor ao implementar o
   gerador (ver "Conflito registrado" acima).

Ver `.claude/skills/gerar-questor/SKILL.md` para o procedimento completo e
`docs/BACKLOG.md` para o próximo passo.
