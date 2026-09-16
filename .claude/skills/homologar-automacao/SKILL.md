---
name: homologar-automacao
description: Conduz o checklist de homologação de uma automação antes de liberá-la para uso em produção pela equipe de DP.
---

# Homologar automação

Use antes de marcar qualquer automação como pronta para operação.

## Checklist

1. **Dados de origem**: os dados usados no teste são de homologação/cópia,
   nunca de produção real sem anonimização/autorização.
2. **Cobertura de testes**: `pytest` passando, incluindo casos de borda e
   regras de negócio confirmadas (ver `.claude/rules/testing.md`).
3. **Rastreabilidade**: a automação gera log suficiente para reconstruir
   entrada → decisão → saída.
4. **Evidência de saída real**: existe pelo menos um exemplo de saída da
   automação que foi validado manualmente por uma pessoa como correto?
   Se não, a homologação não pode ser concluída.
5. **Pendências explícitas**: qualquer código/regra marcado como PENDENTE
   continua bloqueando a geração de arquivos de produção para os casos que
   dependem dele.

## Saída

Registrar o resultado da homologação em `docs/DECISIONS.md` via
`/registrar-decisao`, indicando data, o que foi validado e por quem.
Somente após esse registro a automação pode ser promovida de
"bloqueada" para "liberada" em `state/tasks.json`.
