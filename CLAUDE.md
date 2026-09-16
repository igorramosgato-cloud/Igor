# JR DP Automation Hub

Contexto permanente do projeto de automação do Departamento Pessoal da JR.
Este arquivo é enxuto de propósito. Regras específicas ficam em `.claude/rules/`
e procedimentos executáveis em `.claude/skills/`.

## Metodologia

Todo processo segue, nesta ordem:

dados → estruturação → mapeamento → validação → automação → QA → operação

Nenhuma etapa é pulada. Uma automação não entra em operação sem ter passado
por QA com evidência registrada.

## Regras permanentes (não negociáveis)

1. **Não automatizar processo mal compreendido.** Se o fluxo de origem (ex.:
   layout do importador, planilha-fonte, regra de negócio) não está mapeado
   com evidência física, a tarefa fica `BLOCKED` — nunca "inventada".
2. **Não trabalhar em produção durante homologação.** Toda automação nova
   roda contra dados de homologação/cópia até aprovação explícita.
3. **Não fazer matching ambíguo.** Se a chave de correspondência entre
   sistemas (ex.: matrícula, CPF, nome) não é única e confiável, a
   automação para e reporta o conflito em vez de adivinhar.
4. **Preservar rastreabilidade.** Toda automação registra logs suficientes
   para reconstruir o que foi lido, decidido e gravado.
5. **Preferir arquivo/API/importador a cliques.** RPA de UI é o último
   recurso, não o primeiro.
6. **Validar fonte oficial em matéria regulatória.** Nenhuma regra
   trabalhista/previdenciária é aplicada sem referência à fonte oficial
   (lei, CCT, portaria) registrada em `docs/SOURCE_REGISTRY.md`.

## Como retomar o projeto

Ao iniciar uma sessão, execute `/retomar-projeto`. Isso carrega:

- `state/PROJECT_STATE.md`
- `state/tasks.json`
- `docs/DECISIONS.md`
- este arquivo

## Roadmap (ordem de execução)

1. Variáveis + Benefícios → Questor
2. Auditoria Questor × Sankhya
3. Auditoria automática da folha
4. Admissões
5. Auditoria de consignado
6. eSocial/XML
7. Fechamento mensal automatizado
8. Organização documental
9. Monitoramento CCT/regras

## Regras modulares

- `.claude/rules/governanca.md` — governança de fontes e decisões
- `.claude/rules/testing.md` — padrão de QA e cobertura mínima
- `.claude/rules/matching.md` — regras de correspondência entre sistemas
- `.claude/rules/regulatorio.md` — validação de fonte oficial
- `.claude/rules/art-latex.md` — regras do cliente ART LATEX
- `.claude/rules/questor-sankhya.md` — integração Questor/Sankhya
- `.claude/rules/homologacao-dados.md` — proteção de dados em `homologacao/`
