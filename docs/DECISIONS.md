# Decisões

Entradas mais recentes no topo. Formato definido em
`.claude/skills/registrar-decisao/SKILL.md`.

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
