---
name: retomar-projeto
description: Retoma o contexto do JR DP Automation Hub no início de uma sessão, lendo o estado salvo do projeto em vez de exigir que o usuário reexplique o histórico.
---

# Retomar projeto

Ao ser invocada, leia nesta ordem e resuma para o usuário em poucas linhas
(não repita tudo, apenas o essencial e o próximo passo):

1. `CLAUDE.md` — regras permanentes e roadmap
2. `state/PROJECT_STATE.md` — onde o projeto está agora
3. `state/tasks.json` — tarefas abertas/bloqueadas
4. `docs/DECISIONS.md` — decisões já tomadas (para não perguntar de novo)

Depois de ler, responda ao usuário com:

- em qual processo do roadmap o projeto está (ver `CLAUDE.md`);
- o que está `BLOCKED` e por quê (citando exatamente o que falta);
- qual é a próxima ação recomendada.

Não repetir explicações de metodologia já fixadas em `CLAUDE.md` — assuma
que o usuário já sabe, a menos que ele pergunte.
