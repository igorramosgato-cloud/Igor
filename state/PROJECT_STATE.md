# Estado do projeto

**Atualizado em:** 2026-09-17

## Onde estamos

Roadmap item 1 (Variáveis + Benefícios → Questor, cliente ART LATEX) em
andamento. **181/181 testes passando** (excluindo os dois arquivos com
dependências ausentes no ambiente).

Quatro decisões de arquitetura fecharam os itens que ficariam
esperando indefinidamente por evidência externa:

1. **Eventos da Matriz sem código** — continuam `PENDENTE` (sem
   analogia com a Filial).
2. **De-para manual homologado** (`src/jrdp/depara.py`) — resolve nomes
   não encontrados sem fuzzy automático. Ordem travada:
   `match exato normalizado → de-para homologado → NOT_FOUND/AMBIGUOUS`.
   Arquivo real fica fora do Git (confirmado com `git add -A -n`).
3. **CSV tipo H e versão do Questor** — continuam `PENDENTE`, sem travar
   o resto.
4. **Fail-closed por evento, não pelo pacote** — `src/jrdp/manifesto.py`
   gera `PASS`/`BLOCKED` por evento; um evento 100% resolvido não fica
   refém de outro bloqueado, e nenhum evento gera arquivo parcial.

Também implementados: `sugestao_fuzzy.py` (diagnóstico humano, nunca
decide matching automaticamente) e `identidade.py` (consolida NOT_FOUND
de múltiplos eventos por pessoa, não por registro).

**Validação real agregada** (nenhum dado individual persistido): dos 5
eventos já processados, a soma bruta de não encontrados é 74, mas
consolidando por pessoa são **60 únicas** (11 aparecem em mais de um
evento — confirma a hipótese de que a mesma pessoa se repete entre
abas). Diagnóstico fuzzy: 39 das 60 têm candidato plausível, 21 não.
Manifesto do pacote, sem de-para homologado ainda: `TOTALMENTE
BLOQUEADO` (0/5 eventos gerados) — esperado, falta o trabalho humano de
aprovar as correções.

Continuam PENDENTES: certificação binária tipo H, versão do Questor,
Vale-transporte, códigos de evento da Matriz para 4 abas.

Detalhes completos em `docs/P01_ART_LATEX_QUESTOR.md` e
`docs/DECISIONS.md` (entradas de 2026-09-17). Nenhum dado pessoal foi
reproduzido em qualquer lugar versionado. Nenhum exportador ligado à
produção — `BLOCKED` global do P01 continua valendo.

## Próximo passo

Trabalho humano, não de código: um analista de DP revisa as 60 pessoas
únicas não encontradas (usando os candidatos de diagnóstico fuzzy como
ponto de partida, nunca como aprovação automática) e cria entradas
homologadas em `homologacao/art_latex/questor/depara/depara_nomes.json`
(local, com evidência/aprovador/data). Depois disso, reexecutar a
validação — os eventos que ficarem 100% resolvidos podem ser gerados
pelo `QuestorExporterV`, mesmo que outros continuem bloqueados.

Em paralelo: confirmar códigos de evento da Matriz (4 abas), obter CSV
tipo H real, e a versão do Questor, quando disponíveis.

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
